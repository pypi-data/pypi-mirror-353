"""市场数据服务模块。

提供加密货币市场数据获取、处理和存储功能。
"""

import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from contextlib import nullcontext
from datetime import datetime, timedelta
from decimal import Decimal
from pathlib import Path
from threading import Lock
from typing import Any

import pandas as pd
from rich.logging import RichHandler
from rich.progress import (
    BarColumn,
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from cryptoservice.client import BinanceClientFactory
from cryptoservice.config import settings
from cryptoservice.data import MarketDB
from cryptoservice.exceptions import (
    InvalidSymbolError,
    MarketDataFetchError,
    RateLimitError,
)
from cryptoservice.interfaces import IMarketDataService
from cryptoservice.models import (
    DailyMarketTicker,
    Freq,
    HistoricalKlinesType,
    KlineMarketTicker,
    PerpetualMarketTicker,
    SortBy,
    SymbolTicker,
    UniverseConfig,
    UniverseDefinition,
    UniverseSnapshot,
)
from cryptoservice.utils import DataConverter

# 配置 rich logger
logging.basicConfig(
    level=logging.INFO,
    format="%(message)s",
    handlers=[RichHandler(rich_tracebacks=True)],
)
logger = logging.getLogger(__name__)

cache_lock = Lock()


class MarketDataService(IMarketDataService):
    """市场数据服务实现类。"""

    def __init__(self, api_key: str, api_secret: str) -> None:
        """初始化市场数据服务。

        Args:
            api_key: 用户API密钥
            api_secret: 用户API密钥
        """
        self.client = BinanceClientFactory.create_client(api_key, api_secret)
        self.converter = DataConverter()
        self.db: MarketDB | None = None

    def _validate_and_prepare_path(
        self, path: Path | str, is_file: bool = False, file_name: str | None = None
    ) -> Path:
        """验证并准备路径。

        Args:
            path: 路径字符串或Path对象
            is_file: 是否为文件路径
            file_name: 文件名
        Returns:
            Path: 验证后的Path对象

        Raises:
            ValueError: 路径为空或无效时
        """
        if not path:
            raise ValueError("路径不能为空，必须手动指定")

        path_obj = Path(path)

        # 如果是文件路径，确保父目录存在
        if is_file:
            if path_obj.is_dir():
                path_obj = path_obj.joinpath(file_name) if file_name else path_obj
            else:
                path_obj.parent.mkdir(parents=True, exist_ok=True)
        else:
            # 如果是目录路径，确保目录存在
            path_obj.mkdir(parents=True, exist_ok=True)

        return path_obj

    def get_symbol_ticker(self, symbol: str | None = None) -> SymbolTicker | list[SymbolTicker]:
        """获取单个或所有交易对的行情数据。

        Args:
            symbol: 交易对名称

        Returns:
            SymbolTicker | list[SymbolTicker]: 单个交易对的行情数据或所有交易对的行情数据
        """
        try:
            ticker = self.client.get_symbol_ticker(symbol=symbol)
            if not ticker:
                raise InvalidSymbolError(f"Invalid symbol: {symbol}")

            if isinstance(ticker, list):
                return [SymbolTicker.from_binance_ticker(t) for t in ticker]
            return SymbolTicker.from_binance_ticker(ticker)

        except Exception as e:
            logger.error(f"[red]Error fetching ticker for {symbol}: {e}[/red]")
            raise MarketDataFetchError(f"Failed to fetch ticker: {e}") from e

    def get_perpetual_symbols(
        self, only_trading: bool = True, quote_asset: str = "USDT"
    ) -> list[str]:
        """获取当前市场上所有永续合约交易对。

        Args:
            only_trading: 是否只返回当前可交易的交易对
            quote_asset: 基准资产，默认为USDT，只返回以该资产结尾的交易对

        Returns:
            list[str]: 永续合约交易对列表
        """
        try:
            logger.info(f"获取当前永续合约交易对列表（筛选条件：{quote_asset}结尾）")
            futures_info = self.client.futures_exchange_info()
            perpetual_symbols = [
                symbol["symbol"]
                for symbol in futures_info["symbols"]
                if symbol["contractType"] == "PERPETUAL"
                and (not only_trading or symbol["status"] == "TRADING")
                and symbol["symbol"].endswith(quote_asset)
            ]

            logger.info(f"找到 {len(perpetual_symbols)} 个{quote_asset}永续合约交易对")
            return perpetual_symbols

        except Exception as e:
            logger.error(f"[red]获取永续合约交易对失败: {e}[/red]")
            raise MarketDataFetchError(f"获取永续合约交易对失败: {e}") from e

    def _date_to_timestamp_range(self, date: str) -> tuple[str, str]:
        """将日期字符串转换为时间戳范围（开始和结束）。

        Args:
            date: 日期字符串，格式为 'YYYY-MM-DD'

        Returns:
            tuple[str, str]: (开始时间戳, 结束时间戳)，都是毫秒级时间戳字符串
            - 开始时间戳: 当天的 00:00:00
            - 结束时间戳: 当天的 23:59:59
        """
        start_time = int(
            datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        )
        end_time = int(
            datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        )
        return str(start_time), str(end_time)

    def _date_to_timestamp_start(self, date: str) -> str:
        """将日期字符串转换为当天开始的时间戳。

        Args:
            date: 日期字符串，格式为 'YYYY-MM-DD'

        Returns:
            str: 当天 00:00:00 的毫秒级时间戳字符串
        """
        timestamp = int(
            datetime.strptime(f"{date} 00:00:00", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        )
        return str(timestamp)

    def _date_to_timestamp_end(self, date: str) -> str:
        """将日期字符串转换为当天结束的时间戳。

        Args:
            date: 日期字符串，格式为 'YYYY-MM-DD'

        Returns:
            str: 当天 23:59:59 的毫秒级时间戳字符串
        """
        timestamp = int(
            datetime.strptime(f"{date} 23:59:59", "%Y-%m-%d %H:%M:%S").timestamp() * 1000
        )
        return str(timestamp)

    def check_symbol_exists_on_date(self, symbol: str, date: str) -> bool:
        """检查指定日期是否存在该交易对。

        Args:
            symbol: 交易对名称
            date: 日期，格式为 'YYYY-MM-DD'

        Returns:
            bool: 是否存在该交易对
        """
        try:
            # 将日期转换为时间戳范围
            start_time, end_time = self._date_to_timestamp_range(date)

            # 尝试获取该时间范围内的K线数据
            klines = self.client.futures_klines(
                symbol=symbol,
                interval="1d",
                startTime=start_time,
                endTime=end_time,
                limit=1,
            )

            # 如果有数据，说明该日期存在该交易对
            return bool(klines and len(klines) > 0)

        except Exception as e:
            logger.debug(f"检查交易对 {symbol} 在 {date} 是否存在时出错: {e}")
            return False

    def get_top_coins(
        self,
        limit: int = settings.DEFAULT_LIMIT,
        sort_by: SortBy = SortBy.QUOTE_VOLUME,
        quote_asset: str | None = None,
    ) -> list[DailyMarketTicker]:
        """获取前N个交易对。

        Args:
            limit: 数量
            sort_by: 排序方式
            quote_asset: 基准资产

        Returns:
            list[DailyMarketTicker]: 前N个交易对
        """
        try:
            tickers = self.client.get_ticker()
            market_tickers = [DailyMarketTicker.from_binance_ticker(t) for t in tickers]

            if quote_asset:
                market_tickers = [t for t in market_tickers if t.symbol.endswith(quote_asset)]

            return sorted(
                market_tickers,
                key=lambda x: getattr(x, sort_by.value),
                reverse=True,
            )[:limit]

        except Exception as e:
            logger.error(f"[red]Error getting top coins: {e}[/red]")
            raise MarketDataFetchError(f"Failed to get top coins: {e}") from e

    def get_market_summary(self, interval: Freq = Freq.d1) -> dict[str, Any]:
        """获取市场概览。

        Args:
            interval: 时间间隔

        Returns:
            dict[str, Any]: 市场概览
        """
        try:
            summary: dict[str, Any] = {"snapshot_time": datetime.now(), "data": {}}
            tickers_result = self.get_symbol_ticker()
            if isinstance(tickers_result, list):
                tickers = [ticker.to_dict() for ticker in tickers_result]
            else:
                tickers = [tickers_result.to_dict()]
            summary["data"] = tickers

            return summary

        except Exception as e:
            logger.error(f"[red]Error getting market summary: {e}[/red]")
            raise MarketDataFetchError(f"Failed to get market summary: {e}") from e

    def get_historical_klines(
        self,
        symbol: str,
        start_time: str | datetime,
        end_time: str | datetime | None = None,
        interval: Freq = Freq.h1,
        klines_type: HistoricalKlinesType = HistoricalKlinesType.SPOT,
    ) -> list[KlineMarketTicker]:
        """获取历史行情数据。

        Args:
            symbol: 交易对名称
            start_time: 开始时间
            end_time: 结束时间，如果为None则为当前时间
            interval: 时间间隔
            klines_type: K线类型（现货或期货）

        Returns:
            list[KlineMarketTicker]: 历史行情数据
        """
        try:
            # 处理时间格式
            if isinstance(start_time, str):
                start_time = datetime.fromisoformat(start_time)
            if end_time is None:
                end_time = datetime.now()
            elif isinstance(end_time, str):
                end_time = datetime.fromisoformat(end_time)

            # 转换为时间戳
            start_ts = self._date_to_timestamp_start(start_time.strftime("%Y-%m-%d"))
            end_ts = self._date_to_timestamp_end(end_time.strftime("%Y-%m-%d"))

            logger.info(f"获取 {symbol} 的历史数据 ({interval.value})")

            # 根据klines_type选择API
            if klines_type == HistoricalKlinesType.FUTURES:
                klines = self.client.futures_klines(
                    symbol=symbol,
                    interval=interval.value,
                    startTime=start_ts,
                    endTime=end_ts,
                    limit=1500,
                )
            else:  # SPOT
                klines = self.client.get_klines(
                    symbol=symbol,
                    interval=interval.value,
                    startTime=start_ts,
                    endTime=end_ts,
                    limit=1500,
                )

            data = list(klines)
            if not data:
                logger.warning(f"未找到交易对 {symbol} 在指定时间段内的数据")
                return []

            # 转换为KlineMarketTicker对象
            return [
                KlineMarketTicker(
                    symbol=symbol,
                    last_price=Decimal(str(kline[4])),  # 收盘价作为最新价格
                    open_price=Decimal(str(kline[1])),
                    high_price=Decimal(str(kline[2])),
                    low_price=Decimal(str(kline[3])),
                    volume=Decimal(str(kline[5])),
                    close_time=kline[6],
                )
                for kline in data
            ]

        except Exception as e:
            logger.error(f"[red]Error getting historical data for {symbol}: {e}[/red]")
            raise MarketDataFetchError(f"Failed to get historical data: {e}") from e

    def _fetch_symbol_data(
        self,
        symbol: str,
        start_ts: str,
        end_ts: str,
        interval: Freq,
        klines_type: HistoricalKlinesType = HistoricalKlinesType.FUTURES,
    ) -> list[PerpetualMarketTicker]:
        """获取单个交易对的数据.

        Args:
            symbol: 交易对名称
            start_ts: 开始时间戳 (毫秒)
            end_ts: 结束时间戳 (毫秒)
            interval: 时间间隔
            klines_type: 行情类型
        """
        try:
            # 检查交易对是否在指定日期存在
            if start_ts and end_ts:
                # 将时间戳转换为日期字符串进行验证
                start_date = datetime.fromtimestamp(int(start_ts) / 1000).strftime("%Y-%m-%d")
                if not self.check_symbol_exists_on_date(symbol, start_date):
                    logger.warning(
                        f"交易对 {symbol} 在开始日期 {start_date} 不存在或没有交易数据，"
                        "尝试获取可用数据"
                    )
                    # 不再抛出异常，而是继续执行，让API返回有效的数据范围

            klines = self.client.futures_klines(
                symbol=symbol,
                interval=interval.value,
                startTime=start_ts,
                endTime=end_ts,
                limit=1500,
            )

            data = list(klines)
            if not data:
                logger.warning(f"未找到交易对 {symbol} 在 {start_ts} 到 {end_ts} 之间的数据")
                return []  # 返回空列表而不是抛出异常

            # 处理有数据的情况
            return [
                PerpetualMarketTicker(
                    symbol=symbol,
                    open_time=kline[0],
                    raw_data=kline,  # 保存原始数据
                )
                for kline in data
            ]

        except InvalidSymbolError:
            # 交易对不存在的情况直接重新抛出
            raise
        except Exception as e:
            logger.warning(f"获取交易对 {symbol} 数据时出错: {e}")
            if "Invalid symbol" in str(e):
                raise InvalidSymbolError(f"无效的交易对: {symbol}") from e
            else:
                # 对于其他异常，仍然抛出以便上层处理
                raise MarketDataFetchError(f"获取交易对 {symbol} 数据失败: {e}") from e

    def get_perpetual_data(
        self,
        symbols: list[str],
        start_time: str,
        db_path: Path | str,
        end_time: str | None = None,
        interval: Freq = Freq.m1,
        max_workers: int = 1,
        max_retries: int = 3,
        progress: Progress | None = None,
    ) -> None:
        """获取永续合约数据并存储.

        Args:
            symbols: 交易对列表
            start_time: 开始时间 (YYYY-MM-DD)
            db_path: 数据库文件路径 (必须指定，如: /path/to/market.db)
            end_time: 结束时间 (YYYY-MM-DD)
            interval: 时间间隔
            max_workers: 最大线程数
            max_retries: 最大重试次数
            progress: 进度显示器
        """
        try:
            if not symbols:
                raise ValueError("Symbols list cannot be empty")

            # 验证并准备数据库文件路径
            db_file_path = self._validate_and_prepare_path(db_path, is_file=True)
            end_time = end_time or datetime.now().strftime("%Y-%m-%d")

            # 将日期字符串转换为时间戳
            start_ts = self._date_to_timestamp_start(start_time)
            end_ts = self._date_to_timestamp_end(end_time)

            # 初始化数据库连接 - 直接使用指定的数据库文件路径
            if self.db is None:
                self.db = MarketDB(str(db_file_path))

            # 如果没有传入progress，创建一个默认的
            if progress is None:
                progress = Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    BarColumn(),
                    TimeElapsedColumn(),
                )

            def process_symbol(symbol: str) -> None:
                """处理单个交易对的数据获取。"""
                retry_count = 0
                while retry_count < max_retries:
                    try:
                        data = self._fetch_symbol_data(
                            symbol=symbol,
                            start_ts=start_ts,
                            end_ts=end_ts,
                            interval=interval,
                        )

                        if data:
                            # 确保 db 不为 None
                            if self.db is None:
                                raise MarketDataFetchError("Database pool is not initialized")
                            self.db.store_data(data, interval)  # 直接传递 data，不需要包装成列表
                            return
                        else:
                            logger.info(f"交易对 {symbol} 在指定时间段内无数据")
                            return

                    except InvalidSymbolError as e:
                        # 对于交易对不存在的情况，记录信息后直接返回，不需要重试
                        logger.warning(f"跳过交易对 {symbol}: {e}")
                        return
                    except RateLimitError:
                        wait_time = min(2**retry_count + 1, 30)
                        logger.warning(f"频率限制 - {symbol}: 等待 {wait_time} 秒")
                        time.sleep(wait_time)
                        retry_count += 1
                    except Exception as e:
                        # 检查是否是API频率限制错误
                        if "Too many requests" in str(e) or "APIError" in str(e):
                            wait_time = min(2**retry_count + 10, 60)
                            logger.warning(f"API错误 - {symbol}: 等待 {wait_time} 秒后重试")
                            time.sleep(wait_time)
                            retry_count += 1
                        elif retry_count < max_retries - 1:
                            retry_count += 1
                            logger.warning(f"重试 {retry_count}/{max_retries} - {symbol}: {str(e)}")
                            time.sleep(2)  # 增加基础延迟
                        else:
                            logger.error(f"处理失败 - {symbol}: {str(e)}")
                            break

            with progress if progress is not None else nullcontext():
                overall_task = (
                    progress.add_task("[cyan]处理所有交易对", total=len(symbols))
                    if progress
                    else None
                )

                # 使用线程池并行处理
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = [executor.submit(process_symbol, symbol) for symbol in symbols]

                    # 跟踪完成进度
                    for future in as_completed(futures):
                        try:
                            future.result()
                            if progress and overall_task is not None:
                                progress.update(overall_task, advance=1)
                        except Exception as e:
                            logger.error(f"处理失败: {e}")

            logger.info("✅ Universe数据下载完成!")
            logger.info(f"📁 数据已保存到: {db_file_path}")

        except Exception as e:
            logger.error(f"Failed to fetch perpetual data: {e}")
            raise MarketDataFetchError(f"Failed to fetch perpetual data: {e}") from e

    def define_universe(
        self,
        start_date: str,
        end_date: str,
        t1_months: int,
        t2_months: int,
        t3_months: int,
        top_k: int,
        output_path: Path | str,
        description: str | None = None,
        delay_days: int = 7,
        api_delay_seconds: float = 1.0,
        batch_delay_seconds: float = 3.0,
        batch_size: int = 5,
        quote_asset: str = "USDT",
    ) -> UniverseDefinition:
        """定义universe并保存到文件.

        Args:
            start_date: 开始日期 (YYYY-MM-DD 或 YYYYMMDD)
            end_date: 结束日期 (YYYY-MM-DD 或 YYYYMMDD)
            t1_months: T1时间窗口（月），用于计算mean daily amount
            t2_months: T2滚动频率（月），universe重新选择的频率
            t3_months: T3合约最小创建时间（月），用于筛除新合约
            top_k: 选取的top合约数量
            output_path: universe输出文件路径 (必须指定)
            description: 描述信息
            delay_days: 在重新平衡日期前额外往前推的天数，默认7天
            api_delay_seconds: 每个API请求之间的延迟秒数，默认1.0秒
            batch_delay_seconds: 每批次请求之间的延迟秒数，默认3.0秒
            batch_size: 每批次的请求数量，默认5个
            quote_asset: 基准资产，默认为USDT，只筛选以该资产结尾的交易对

        Returns:
            UniverseDefinition: 定义的universe
        """
        try:
            # 验证并准备输出路径
            output_path_obj = self._validate_and_prepare_path(
                output_path,
                is_file=True,
                file_name=(
                    f"universe_{start_date}_{end_date}_{t1_months}_"
                    f"{t2_months}_{t3_months}_{top_k}.json"
                ),
            )

            # 标准化日期格式
            start_date = self._standardize_date_format(start_date)
            end_date = self._standardize_date_format(end_date)

            # 创建配置
            config = UniverseConfig(
                start_date=start_date,
                end_date=end_date,
                t1_months=t1_months,
                t2_months=t2_months,
                t3_months=t3_months,
                top_k=top_k,
            )

            logger.info(f"开始定义universe: {start_date} 到 {end_date}")
            logger.info(
                f"参数: T1={t1_months}月, T2={t2_months}月, T3={t3_months}月, Top-K={top_k}"
            )

            # 生成重新选择日期序列 (每T2个月)
            # 从起始日期开始，每隔T2个月生成重平衡日期，表示universe重新选择的时间点
            rebalance_dates = self._generate_rebalance_dates(start_date, end_date, t2_months)

            logger.info("重平衡计划:")
            logger.info(f"  - 时间范围: {start_date} 到 {end_date}")
            logger.info(f"  - 重平衡间隔: 每{t2_months}个月")
            logger.info(f"  - 数据延迟: {delay_days}天")
            logger.info(f"  - T1数据窗口: {t1_months}个月")
            logger.info(f"  - 重平衡日期: {rebalance_dates}")

            if not rebalance_dates:
                raise ValueError("无法生成重平衡日期，请检查时间范围和T2参数")

            # 收集所有周期的snapshots
            all_snapshots = []

            # 在每个重新选择日期计算universe
            for i, rebalance_date in enumerate(rebalance_dates):
                logger.info(f"处理日期 {i + 1}/{len(rebalance_dates)}: {rebalance_date}")

                # 计算基准日期（重新平衡日期前delay_days天）
                base_date = pd.to_datetime(rebalance_date) - timedelta(days=delay_days)
                base_date_str = base_date.strftime("%Y-%m-%d")

                # 计算T1回看期间的开始日期（从base_date往前推T1个月）
                calculated_t1_start = self._subtract_months(base_date_str, t1_months)

                logger.info(
                    f"周期 {i + 1}: 基准日期={base_date_str} (重新平衡日期前{delay_days}天), "
                    f"T1数据期间={calculated_t1_start} 到 {base_date_str}"
                )

                # 获取符合条件的交易对和它们的mean daily amount
                universe_symbols, mean_amounts = self._calculate_universe_for_date(
                    rebalance_date=base_date_str,  # 使用基准日期作为计算终点
                    t1_start_date=calculated_t1_start,
                    t3_months=t3_months,
                    top_k=top_k,
                    api_delay_seconds=api_delay_seconds,
                    batch_delay_seconds=batch_delay_seconds,
                    batch_size=batch_size,
                    quote_asset=quote_asset,
                )

                # 创建该周期的snapshot
                # 计算时间戳
                start_ts = self._date_to_timestamp_start(calculated_t1_start)
                end_ts = self._date_to_timestamp_end(base_date_str)

                snapshot = UniverseSnapshot.create_with_dates_and_timestamps(
                    effective_date=rebalance_date,  # 使用原始重新平衡日期
                    period_start_date=calculated_t1_start,
                    period_end_date=base_date_str,  # 使用基准日期作为数据结束日期
                    period_start_ts=start_ts,
                    period_end_ts=end_ts,
                    symbols=universe_symbols,
                    mean_daily_amounts=mean_amounts,
                    metadata={
                        "t1_start_date": calculated_t1_start,
                        "base_date": base_date_str,
                        "delay_days": delay_days,
                        "quote_asset": quote_asset,
                        "selected_symbols_count": len(universe_symbols),
                    },
                )

                all_snapshots.append(snapshot)

                logger.info(f"✅ 日期 {rebalance_date}: 选择了 {len(universe_symbols)} 个交易对")

            # 创建完整的universe定义
            universe_def = UniverseDefinition(
                config=config,
                snapshots=all_snapshots,
                creation_time=datetime.now(),
                description=description,
            )

            # 保存汇总的universe定义
            universe_def.save_to_file(output_path_obj)

            logger.info("🎉 Universe定义完成！")
            logger.info(f"📁 包含 {len(all_snapshots)} 个重新平衡周期")
            logger.info(f"📋 汇总文件: {output_path_obj}")

            return universe_def

        except Exception as e:
            logger.error(f"[red]定义universe失败: {e}[/red]")
            raise MarketDataFetchError(f"定义universe失败: {e}") from e

    def _standardize_date_format(self, date_str: str) -> str:
        """标准化日期格式为 YYYY-MM-DD。"""
        if len(date_str) == 8:  # YYYYMMDD
            return f"{date_str[:4]}-{date_str[4:6]}-{date_str[6:8]}"
        return date_str

    def _generate_rebalance_dates(
        self, start_date: str, end_date: str, t2_months: int
    ) -> list[str]:
        """生成重新选择universe的日期序列。

        从起始日期开始，每隔T2个月生成重平衡日期，这些日期表示universe重新选择的时间点。

        Args:
            start_date: 开始日期
            end_date: 结束日期
            t2_months: 重新平衡间隔（月）

        Returns:
            list[str]: 重平衡日期列表
        """
        dates = []
        start_date_obj = pd.to_datetime(start_date)
        end_date_obj = pd.to_datetime(end_date)

        # 从起始日期开始，每隔T2个月生成重平衡日期
        current_date = start_date_obj

        while current_date <= end_date_obj:
            dates.append(current_date.strftime("%Y-%m-%d"))
            current_date = current_date + pd.DateOffset(months=t2_months)

        return dates

    def _subtract_months(self, date_str: str, months: int) -> str:
        """从日期减去指定月数。"""
        date_obj = pd.to_datetime(date_str)
        # 使用pandas的DateOffset来正确处理月份边界问题
        result_date = date_obj - pd.DateOffset(months=months)
        return str(result_date.strftime("%Y-%m-%d"))

    def _get_available_symbols_for_period(
        self, start_date: str, end_date: str, quote_asset: str = "USDT"
    ) -> list[str]:
        """获取指定时间段内实际可用的永续合约交易对。

        Args:
            start_date: 开始日期
            end_date: 结束日期
            quote_asset: 基准资产，用于筛选交易对

        Returns:
            list[str]: 在该时间段内有数据的交易对列表
        """
        try:
            # 先获取当前所有永续合约作为候选（筛选指定的基准资产）
            candidate_symbols = self.get_perpetual_symbols(
                only_trading=True, quote_asset=quote_asset
            )
            logger.info(
                f"检查 {len(candidate_symbols)} 个{quote_asset}候选交易对在 {start_date} 到 "
                f"{end_date} 期间的可用性..."
            )

            available_symbols = []
            batch_size = 50
            for i in range(0, len(candidate_symbols), batch_size):
                batch = candidate_symbols[i : i + batch_size]
                for symbol in batch:
                    # 检查在起始日期是否有数据
                    if self.check_symbol_exists_on_date(symbol, start_date):
                        available_symbols.append(symbol)

                # 显示进度
                processed = min(i + batch_size, len(candidate_symbols))
                logger.info(
                    f"已检查 {processed}/{len(candidate_symbols)} 个交易对，"
                    f"找到 {len(available_symbols)} 个可用交易对"
                )

                # 避免API频率限制
                time.sleep(0.1)

            logger.info(
                f"在 {start_date} 到 {end_date} 期间找到 {len(available_symbols)} "
                f"个可用的{quote_asset}永续合约交易对"
            )
            return available_symbols

        except Exception as e:
            logger.warning(f"获取可用交易对时出错: {e}")
            # 如果API检查失败，返回当前所有永续合约
            return self.get_perpetual_symbols(only_trading=True, quote_asset=quote_asset)

    def _calculate_universe_for_date(
        self,
        rebalance_date: str,
        t1_start_date: str,
        t3_months: int,
        top_k: int,
        api_delay_seconds: float = 1.0,
        batch_delay_seconds: float = 3.0,
        batch_size: int = 5,
        quote_asset: str = "USDT",
    ) -> tuple[list[str], dict[str, float]]:
        """计算指定日期的universe。

        Args:
            rebalance_date: 重平衡日期
            t1_start_date: T1开始日期
            t3_months: T3月数
            top_k: 选择的top数量
            api_delay_seconds: 每个API请求之间的延迟秒数
            batch_delay_seconds: 每批次请求之间的延迟秒数
            batch_size: 每批次的请求数量
            quote_asset: 基准资产，用于筛选交易对
        """
        try:
            # 获取在该时间段内实际存在的永续合约交易对
            actual_symbols = self._get_available_symbols_for_period(
                t1_start_date, rebalance_date, quote_asset
            )

            # 筛除新合约 (创建时间不足T3个月的)
            cutoff_date = self._subtract_months(rebalance_date, t3_months)
            eligible_symbols = [
                symbol
                for symbol in actual_symbols
                if self._symbol_exists_before_date(symbol, cutoff_date)
            ]

            if not eligible_symbols:
                logger.warning(f"日期 {rebalance_date}: 没有找到符合条件的交易对")
                return [], {}

            # 通过API获取数据计算mean daily amount
            mean_amounts = {}

            logger.info(f"开始通过API获取 {len(eligible_symbols)} 个交易对的历史数据...")

            for i, symbol in enumerate(eligible_symbols):
                try:
                    # 将日期字符串转换为时间戳
                    start_ts = self._date_to_timestamp_start(t1_start_date)
                    end_ts = self._date_to_timestamp_end(rebalance_date)

                    # 参数化的频率控制
                    if i > 0:  # 第一个请求不需要延迟
                        if i % batch_size == 0:  # 每批次请求延迟更长时间
                            logger.info(
                                f"已处理 {i}/{len(eligible_symbols)} 个交易对，"
                                f"等待{batch_delay_seconds}秒..."
                            )
                            time.sleep(batch_delay_seconds)
                        else:
                            time.sleep(api_delay_seconds)  # 每个请求之间的基础延迟

                    # 获取历史K线数据
                    klines = self._fetch_symbol_data(
                        symbol=symbol,
                        start_ts=start_ts,
                        end_ts=end_ts,
                        interval=Freq.d1,
                    )

                    if klines:
                        # 数据完整性检查
                        expected_days = (
                            pd.to_datetime(rebalance_date) - pd.to_datetime(t1_start_date)
                        ).days + 1
                        actual_days = len(klines)

                        if actual_days < expected_days * 0.8:  # 允许20%的数据缺失
                            logger.warning(
                                f"交易对 {symbol} 数据不完整: 期望{expected_days}天，"
                                f"实际{actual_days}天"
                            )

                        # 计算平均日成交额
                        amounts = []
                        for kline in klines:
                            try:
                                # kline.raw_data[7] 是成交额（USDT）
                                if kline.raw_data and len(kline.raw_data) > 7:
                                    amount = float(kline.raw_data[7])
                                    amounts.append(amount)
                            except (ValueError, IndexError):
                                continue

                        if amounts:
                            mean_amount = sum(amounts) / len(amounts)
                            mean_amounts[symbol] = mean_amount
                        else:
                            logger.warning(f"交易对 {symbol} 在期间内没有有效的成交量数据")

                except RateLimitError:
                    # 遇到频率限制时，等待更长时间后重试
                    logger.warning(f"遇到频率限制，等待60秒后继续处理 {symbol}")
                    time.sleep(60)
                    try:
                        # 重试一次
                        klines = self._fetch_symbol_data(
                            symbol=symbol,
                            start_ts=start_ts,
                            end_ts=end_ts,
                            interval=Freq.d1,
                        )
                        # ... 处理数据的代码保持相同
                    except Exception:
                        logger.warning(f"重试后仍然失败，跳过 {symbol}")
                        continue
                except Exception as e:
                    logger.warning(f"获取 {symbol} 数据时出错，跳过: {e}")
                    # 如果是API错误，增加延迟
                    if "Too many requests" in str(e) or "APIError" in str(e):
                        logger.info("检测到API错误，增加延迟时间")
                        time.sleep(5)
                    continue

            # 按mean daily amount排序并选择top_k
            if mean_amounts:
                sorted_symbols = sorted(mean_amounts.items(), key=lambda x: x[1], reverse=True)
                top_symbols = sorted_symbols[:top_k]

                universe_symbols = [symbol for symbol, _ in top_symbols]
                final_amounts = dict(top_symbols)

                # 显示选择结果
                if len(universe_symbols) <= 10:
                    logger.info(f"选中的交易对: {universe_symbols}")
                else:
                    logger.info(f"Top 5: {universe_symbols[:5]}")
                    logger.info("完整列表已保存到文件中")
            else:
                # 如果没有可用数据，至少返回前top_k个eligible symbols
                universe_symbols = eligible_symbols[:top_k]
                final_amounts = dict.fromkeys(universe_symbols, 0.0)
                logger.warning(f"无法通过API获取数据，返回前{len(universe_symbols)}个交易对")

            return universe_symbols, final_amounts

        except Exception as e:
            logger.error(f"计算日期 {rebalance_date} 的universe时出错: {e}")
            return [], {}

    def _symbol_exists_before_date(self, symbol: str, cutoff_date: str) -> bool:
        """检查交易对是否在指定日期之前就存在。"""
        try:
            # 检查在cutoff_date之前是否有数据
            # 这里我们检查cutoff_date前一天的数据
            check_date = (pd.to_datetime(cutoff_date) - timedelta(days=1)).strftime("%Y-%m-%d")
            return self.check_symbol_exists_on_date(symbol, check_date)
        except Exception:
            # 如果检查失败，默认认为存在
            return True

    def download_universe_data(
        self,
        universe_file: Path | str,
        db_path: Path | str,
        data_path: Path | str | None = None,
        interval: Freq = Freq.h1,
        max_workers: int = 4,
        max_retries: int = 3,
        include_buffer_days: int = 7,
        extend_to_present: bool = True,
    ) -> None:
        """根据universe定义文件下载相应的历史数据到数据库。

        Args:
            universe_file: universe定义文件路径 (必须指定)
            db_path: 数据库文件路径 (必须指定，如: /path/to/market.db)
            data_path: 数据文件存储路径 (可选，用于存储其他数据文件)
            interval: 数据频率 (1m, 1h, 4h, 1d等)
            max_workers: 并发线程数
            max_retries: 最大重试次数
            include_buffer_days: 在数据期间前后增加的缓冲天数
            extend_to_present: 是否将数据扩展到当前日期

        Example:
            service.download_universe_data(
                universe_file="/path/to/universe.json",
                db_path="/path/to/database/market.db",
                data_path="/path/to/data",  # 可选
                interval=Freq.h1,
                max_workers=4
            )
        """
        try:
            # 验证路径
            universe_file_obj = self._validate_and_prepare_path(universe_file, is_file=True)
            db_file_path = self._validate_and_prepare_path(db_path, is_file=True)

            # data_path是可选的，如果提供则验证
            data_path_obj = None
            if data_path:
                data_path_obj = self._validate_and_prepare_path(data_path, is_file=False)

            # 检查universe文件是否存在
            if not universe_file_obj.exists():
                raise FileNotFoundError(f"Universe文件不存在: {universe_file_obj}")

            # 加载universe定义
            universe_def = UniverseDefinition.load_from_file(universe_file_obj)

            # 分析数据下载需求
            download_plan = self._analyze_universe_data_requirements(
                universe_def, include_buffer_days, extend_to_present
            )

            logger.info("📊 数据下载计划:")
            logger.info(f"   - 总交易对数: {download_plan['total_symbols']}")
            logger.info(
                f"   - 时间范围: {download_plan['overall_start_date']} 到 "
                f"{download_plan['overall_end_date']}"
            )
            logger.info(f"   - 数据频率: {interval.value}")
            logger.info(f"   - 并发线程: {max_workers}")
            logger.info(f"   - 数据库路径: {db_file_path}")
            if data_path_obj:
                logger.info(f"   - 数据文件路径: {data_path_obj}")

            # 执行数据下载
            self.get_perpetual_data(
                symbols=download_plan["unique_symbols"],
                start_time=download_plan["overall_start_date"],
                end_time=download_plan["overall_end_date"],
                db_path=db_file_path,
                interval=interval,
                max_workers=max_workers,
                max_retries=max_retries,
            )

            logger.info("✅ Universe数据下载完成!")
            logger.info(f"📁 数据已保存到: {db_file_path}")

            # 验证数据完整性
            self._verify_universe_data_integrity(
                universe_def, db_file_path, interval, download_plan
            )

        except Exception as e:
            logger.error(f"[red]下载universe数据失败: {e}[/red]")
            raise MarketDataFetchError(f"下载universe数据失败: {e}") from e

    def _analyze_universe_data_requirements(
        self,
        universe_def: UniverseDefinition,
        buffer_days: int = 7,
        extend_to_present: bool = True,
    ) -> dict[str, Any]:
        """分析universe数据下载需求。

        Args:
            universe_def: Universe定义
            buffer_days: 缓冲天数
            extend_to_present: 是否扩展到当前日期

        Returns:
            Dict: 下载计划详情
        """
        import pandas as pd

        # 收集所有的交易对和时间范围
        all_symbols = set()
        all_dates = []

        for snapshot in universe_def.snapshots:
            all_symbols.update(snapshot.symbols)
            all_dates.extend(
                [
                    snapshot.period_start_date,
                    snapshot.period_end_date,
                    snapshot.effective_date,
                ]
            )

        # 计算总体时间范围
        start_date = pd.to_datetime(min(all_dates)) - timedelta(days=buffer_days)
        end_date = pd.to_datetime(max(all_dates)) + timedelta(days=buffer_days)

        if extend_to_present:
            end_date = max(end_date, pd.to_datetime("today"))

        return {
            "unique_symbols": sorted(all_symbols),
            "total_symbols": len(all_symbols),
            "overall_start_date": start_date.strftime("%Y-%m-%d"),
            "overall_end_date": end_date.strftime("%Y-%m-%d"),
        }

    def _verify_universe_data_integrity(
        self,
        universe_def: UniverseDefinition,
        db_path: Path,
        interval: Freq,
        download_plan: dict[str, Any],
    ) -> None:
        """验证下载的universe数据完整性。

        Args:
            universe_def: Universe定义
            db_path: 数据库文件路径
            interval: 数据频率
            download_plan: 下载计划
        """
        try:
            from cryptoservice.data import MarketDB

            # 初始化数据库连接 - 直接使用数据库文件路径
            db = MarketDB(str(db_path))

            logger.info("🔍 验证数据完整性...")
            incomplete_symbols: list[str] = []
            missing_data: list[dict[str, str]] = []
            successful_snapshots = 0

            for snapshot in universe_def.snapshots:
                try:
                    # 检查该快照的主要交易对数据，使用更宽泛的时间范围
                    # 扩展时间范围以确保能够找到数据
                    period_start = pd.to_datetime(snapshot.period_start_date) - timedelta(days=3)
                    period_end = pd.to_datetime(snapshot.period_end_date) + timedelta(days=3)

                    df = db.read_data(
                        symbols=snapshot.symbols[:3],  # 只检查前3个主要交易对
                        start_time=period_start.strftime("%Y-%m-%d"),
                        end_time=period_end.strftime("%Y-%m-%d"),
                        freq=interval,
                        raise_on_empty=False,  # 不在没有数据时抛出异常
                    )

                    if df is not None and not df.empty:
                        # 检查数据覆盖的交易对数量
                        available_symbols = df.index.get_level_values("symbol").unique()
                        missing_symbols = set(snapshot.symbols[:3]) - set(available_symbols)
                        if missing_symbols:
                            incomplete_symbols.extend(missing_symbols)
                            logger.debug(
                                f"快照 {snapshot.effective_date}缺少交易对: {list(missing_symbols)}"
                            )
                        else:
                            successful_snapshots += 1
                            logger.debug(f"快照 {snapshot.effective_date} 验证成功")
                    else:
                        logger.debug(f"快照 {snapshot.effective_date} 在扩展时间范围内未找到数据")
                        missing_data.append(
                            {
                                "snapshot_date": snapshot.effective_date,
                                "error": "No data in extended time range",
                            }
                        )

                except Exception as e:
                    logger.debug(f"验证快照 {snapshot.effective_date} 时出错: {e}")
                    # 不再记录为严重错误，只是记录调试信息
                    missing_data.append({"snapshot_date": snapshot.effective_date, "error": str(e)})

            # 报告验证结果 - 更友好的报告方式
            total_snapshots = len(universe_def.snapshots)
            success_rate = successful_snapshots / total_snapshots if total_snapshots > 0 else 0

            logger.info("✅ 数据完整性验证完成")
            logger.info(f"   - 已下载交易对: {download_plan['total_symbols']} 个")
            logger.info(
                f"   - 时间范围: {download_plan['overall_start_date']} 到 "
                f"{download_plan['overall_end_date']}"
            )
            logger.info(f"   - 数据频率: {interval.value}")
            logger.info(
                f"   - 成功验证快照: {successful_snapshots}/{total_snapshots} ({success_rate:.1%})"
            )

            # 只有在成功率很低时才给出警告
            if success_rate < 0.5:
                logger.warning(f"⚠️ 验证成功率较低: {success_rate:.1%}")
                if incomplete_symbols:
                    unique_incomplete = set(incomplete_symbols)
                    logger.warning(f"   - 数据不完整的交易对: {len(unique_incomplete)} 个")
                    if len(unique_incomplete) <= 5:
                        logger.warning(f"   - 具体交易对: {list(unique_incomplete)}")

                if missing_data:
                    logger.warning(f"   - 无法验证的快照: {len(missing_data)} 个")
            else:
                logger.info("📊 数据质量良好，建议进行后续分析")

        except Exception as e:
            logger.warning(f"数据完整性验证过程中出现问题，但不影响数据使用: {e}")
            logger.info("💡 提示: 验证失败不代表数据下载失败，可以尝试查询具体数据进行确认")

    def download_universe_data_by_periods(
        self,
        universe_file: Path | str,
        db_path: Path | str,
        data_path: Path | str | None = None,
        interval: Freq = Freq.h1,
        max_workers: int = 4,
        max_retries: int = 3,
        include_buffer_days: int = 7,
    ) -> None:
        """按周期分别下载universe数据（更精确的下载方式）。

        这种方式为每个重平衡周期单独下载数据，可以避免下载不必要的数据。

        Args:
            universe_file: universe定义文件路径 (必须指定)
            db_path: 数据库文件路径 (必须指定，如: /path/to/market.db)
            data_path: 数据文件存储路径 (可选，用于存储其他数据文件)
            interval: 数据频率
            max_workers: 并发线程数
            max_retries: 最大重试次数
            include_buffer_days: 缓冲天数
        """
        try:
            # 验证路径
            universe_file_obj = self._validate_and_prepare_path(universe_file, is_file=True)
            db_file_path = self._validate_and_prepare_path(db_path, is_file=True)

            # data_path是可选的，如果提供则验证
            data_path_obj = None
            if data_path:
                data_path_obj = self._validate_and_prepare_path(data_path, is_file=False)

            # 检查universe文件是否存在
            if not universe_file_obj.exists():
                raise FileNotFoundError(f"Universe文件不存在: {universe_file_obj}")

            # 加载universe定义
            universe_def = UniverseDefinition.load_from_file(universe_file_obj)

            logger.info("📊 按周期下载数据:")
            logger.info(f"   - 总快照数: {len(universe_def.snapshots)}")
            logger.info(f"   - 数据频率: {interval.value}")
            logger.info(f"   - 并发线程: {max_workers}")
            logger.info(f"   - 数据库路径: {db_file_path}")
            if data_path_obj:
                logger.info(f"   - 数据文件路径: {data_path_obj}")

            # 为每个周期单独下载数据
            for i, snapshot in enumerate(universe_def.snapshots):
                logger.info(
                    f"📅 处理快照 {i + 1}/{len(universe_def.snapshots)}: {snapshot.effective_date}"
                )

                # 计算下载时间范围
                start_date = pd.to_datetime(snapshot.period_start_date) - timedelta(
                    days=include_buffer_days
                )
                end_date = pd.to_datetime(snapshot.period_end_date) + timedelta(
                    days=include_buffer_days
                )

                logger.info(f"   - 交易对数量: {len(snapshot.symbols)}")
                logger.info(
                    f"   - 数据期间: {start_date.strftime('%Y-%m-%d')} 到 "
                    f"{end_date.strftime('%Y-%m-%d')}"
                )

                # 下载该周期的数据
                self.get_perpetual_data(
                    symbols=snapshot.symbols,
                    start_time=start_date.strftime("%Y-%m-%d"),
                    end_time=end_date.strftime("%Y-%m-%d"),
                    db_path=db_file_path,
                    interval=interval,
                    max_workers=max_workers,
                    max_retries=max_retries,
                )

                logger.info(f"   ✅ 快照 {snapshot.effective_date} 下载完成")

            logger.info("🎉 所有universe数据下载完成!")
            logger.info(f"📁 数据已保存到: {db_file_path}")

        except Exception as e:
            logger.error(f"[red]按周期下载universe数据失败: {e}[/red]")
            raise MarketDataFetchError(f"按周期下载universe数据失败: {e}") from e
