"""测试 Ctrl+C 响应速度

这个脚本用于测试改进后的 Ctrl+C 信号处理是否能快速响应。
"""

import asyncio
import signal
import time

from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

shutdown = False


def signal_handler(signum, frame):
    """处理 Ctrl+C 信号"""
    global shutdown
    shutdown = True
    logger.info("收到 Ctrl+C 信号，准备退出...")


async def test_interruptible_sleep():
    """测试可中断的等待"""
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("开始测试，按 Ctrl+C 测试响应速度...")
    logger.info("正在模拟长时间运行的策略（每次等待2秒）...")
    
    count = 0
    start_time = time.time()
    
    while not shutdown:
        count += 1
        logger.info(f"执行第 {count} 次循环")
        
        # 可中断的等待（模拟交易间隔）
        interval_seconds = 2
        for _ in range(interval_seconds * 10):
            if shutdown:
                break
            await asyncio.sleep(0.1)
        
        if shutdown:
            elapsed = time.time() - start_time
            logger.info(
                f"从接收信号到退出耗时: {elapsed:.2f} 秒",
                total_cycles=count,
            )
            break


if __name__ == "__main__":
    try:
        asyncio.run(test_interruptible_sleep())
    except KeyboardInterrupt:
        logger.info("KeyboardInterrupt 捕获")
    
    logger.info("程序已退出")

