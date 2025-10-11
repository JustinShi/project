"""运行交易策略

使用配置文件（config/trading_config.yaml）运行交易策略

示例用法:
    # 运行所有启用的策略
    uv run python scripts/run_trading_strategy.py

    # 运行指定策略
    uv run python scripts/run_trading_strategy.py --strategy aop_test

    # 查看策略状态
    uv run python scripts/run_trading_strategy.py --status

    # 使用自定义配置文件
    uv run python scripts/run_trading_strategy.py --config path/to/config.yaml
"""

import argparse
import asyncio
import signal
import sys

from binance.application.services.strategy_executor import StrategyExecutor
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class StrategyRunner:
    """策略运行器"""

    def __init__(self, config_path: str = "config/trading_config.yaml"):
        self.executor = StrategyExecutor(config_path)
        self._shutdown = False

    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        logger.info("收到终止信号，正在停止所有策略...")
        self._shutdown = True

    async def run_all_strategies(self) -> None:
        """运行所有启用的策略"""
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            logger.info("启动所有启用的策略")
            await self.executor.start_all_strategies()
        except Exception as exc:
            logger.error("策略执行异常", error=str(exc))
        finally:
            await self.executor.stop_all_strategies()
            logger.info("所有策略已停止")

    async def run_strategy(self, strategy_id: str) -> None:
        """运行指定策略

        Args:
            strategy_id: 策略ID
        """
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            logger.info("启动策略", strategy_id=strategy_id)
            success = await self.executor.start_strategy(strategy_id)
            if not success:
                logger.error("策略启动失败", strategy_id=strategy_id)
                return

            # 等待策略完成或被中断
            while strategy_id in self.executor._running_tasks and not self._shutdown:
                await asyncio.sleep(1)

        except Exception as exc:
            logger.error("策略执行异常", strategy_id=strategy_id, error=str(exc))
        finally:
            await self.executor.stop_strategy(strategy_id)
            logger.info("策略已停止", strategy_id=strategy_id)

    def show_status(self) -> None:
        """显示策略状态"""
        status_list = self.executor.get_all_strategy_status()

        logger.info("=" * 80)
        logger.info("交易策略状态")
        logger.info("=" * 80)

        for status in status_list:
            logger.info(
                "策略信息",
                strategy_id=status["strategy_id"],
                strategy_name=status["strategy_name"],
                enabled=status["enabled"],
                is_running=status["is_running"],
                target_volume=status["target_volume"],
                total_volume=status["total_volume"],
                progress=f"{status['progress_percentage']:.2f}%",
                user_count=status["user_count"],
                user_volumes=status["user_volumes"],
            )
            logger.info("-" * 80)

        logger.info("=" * 80)


async def main() -> None:
    parser = argparse.ArgumentParser(
        description="交易策略执行器",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  # 运行所有启用的策略
  python scripts/run_trading_strategy.py

  # 运行指定策略
  python scripts/run_trading_strategy.py --strategy aop_test

  # 查看策略状态
  python scripts/run_trading_strategy.py --status

  # 使用自定义配置文件
  python scripts/run_trading_strategy.py --config path/to/config.yaml
        """
    )

    parser.add_argument(
        "--config",
        type=str,
        default="config/trading_config.yaml",
        help="策略配置文件路径（默认: config/trading_config.yaml）",
    )
    parser.add_argument(
        "--strategy",
        type=str,
        help="指定要运行的策略ID（不指定则运行所有启用的策略）",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="显示策略状态",
    )

    args = parser.parse_args()

    # 创建运行器
    runner = StrategyRunner(args.config)

    # 根据参数执行相应操作
    if args.status:
        runner.show_status()
    elif args.strategy:
        await runner.run_strategy(args.strategy)
    else:
        await runner.run_all_strategies()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("用户中断执行")
        sys.exit(0)
    except Exception as e:
        logger.error("程序异常退出", error=str(e))
        sys.exit(1)
