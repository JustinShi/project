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
import os
import signal
import sys
import threading

from binance.application.services.strategy_executor import StrategyExecutor
from binance.infrastructure.logging.logger import get_logger


logger = get_logger(__name__)


class StrategyRunner:
    """策略运行器"""

    def __init__(
        self,
        config_path: str = "config/trading_config.yaml",
    ):
        self.executor = StrategyExecutor(config_path)
        self._shutdown = False
        self._force_exit = False
        self._exit_timer = None

    def _signal_handler(self, signum, frame):
        """处理终止信号"""
        if self._force_exit:
            logger.warning("强制退出，立即终止进程...")
            os._exit(1)

        logger.info("收到终止信号，正在停止所有策略...")
        self._shutdown = True

        # 立即设置强制停止标志
        self.executor._force_stop = True

        # 立即设置所有策略的停止标志
        for strategy_id in self.executor._stop_flags:
            self.executor._stop_flags[strategy_id] = True

        # 设置强制退出定时器（5秒后强制退出，缩短等待时间）
        if self._exit_timer is None:
            self._exit_timer = threading.Timer(5.0, self._force_exit_handler)
            self._exit_timer.start()
            logger.warning("如果5秒内无法正常停止，将强制退出进程")

    def _force_exit_handler(self):
        """强制退出处理器"""
        logger.error("无法在5秒内正常停止，强制退出进程")
        self._force_exit = True
        # 强制终止所有线程和进程
        os._exit(1)

    async def run_all_strategies(self) -> None:
        """运行所有启用的策略"""
        # 注册信号处理器
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        try:
            logger.info("启动所有启用的策略")
            await self.executor.start_all_strategies()

            # 等待所有策略完成或被中断
            # 修改：等待所有策略都完成，而不是任何一个完成就停止
            while self.executor._running_tasks and not self._shutdown:
                # 检查是否所有策略都已完成
                if not self.executor._running_tasks:
                    logger.info("所有策略已完成")
                    break

                await asyncio.sleep(1)

        except KeyboardInterrupt:
            logger.info("收到键盘中断信号")
        except Exception as exc:
            logger.error("策略执行异常", error=str(exc))
        finally:
            # 取消强制退出定时器
            if self._exit_timer:
                self._exit_timer.cancel()
                self._exit_timer = None

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

  # 运行指定策略（带进度条）
  python scripts/run_trading_strategy.py --strategy aop_test --progress

  # 查看策略状态
  python scripts/run_trading_strategy.py --status

  # 使用自定义配置文件
  python scripts/run_trading_strategy.py --config path/to/config.yaml
        """,
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
    parser.add_argument(
        "--quiet",
        action="store_true",
        help="安静模式，只显示最终结果",
    )

    args = parser.parse_args()

    # 安静模式：设置日志级别为WARNING
    if args.quiet:
        import os

        os.environ["LOG_LEVEL"] = "WARNING"

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
    except (OSError, BrokenPipeError):
        # 控制台关闭导致的输出错误，正常退出
        sys.exit(0)
    except Exception as e:
        try:
            logger.error("程序异常退出", error=str(e), error_type=type(e).__name__)
        except (OSError, BrokenPipeError):
            # 如果日志输出也失败，静默退出
            pass
        sys.exit(1)
