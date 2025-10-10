"""测试批次执行逻辑"""

import asyncio
import sys
from pathlib import Path

# 添加项目根目录到路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from binance.infrastructure.logging.logger import get_logger
from binance.application.services.strategy_executor import StrategyExecutor

logger = get_logger(__name__)


async def main():
    """测试批次执行逻辑
    
    测试场景：
    1. 启动 AOP 策略（mulPoint=4）
    2. 目标交易量：100 USDT
    3. 单次金额：40 USDT
    4. 观察批次执行流程
    """
    logger.info("="*80)
    logger.info("批次执行逻辑测试")
    logger.info("="*80)
    
    # 创建执行器
    executor = StrategyExecutor("config/trading_config.yaml")
    
    # 启动策略（这会自动读取配置）
    try:
        logger.info("启动策略执行...")
        await executor.start_all_strategies()
        
    except KeyboardInterrupt:
        logger.info("用户中断执行")
    except Exception as e:
        logger.error(f"执行出错: {e}")
    finally:
        logger.info("测试完成")


if __name__ == "__main__":
    asyncio.run(main())

