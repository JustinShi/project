#!/usr/bin/env python3
"""测试价格WebSocket推送"""

import asyncio
import json
import logging
from datetime import datetime
from decimal import Decimal

from binance.domain.entities.price_data import PriceData
from binance.domain.services.price_volatility_monitor import PriceVolatilityMonitor
from binance.infrastructure.binance_client.price_websocket import PriceWebSocketConnector

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class PriceTestHandler:
    """价格测试处理器"""
    
    def __init__(self):
        self.price_count = 0
        self.volatility_alerts = 0
        self.monitor = PriceVolatilityMonitor(
            window_size=10,  # 10个数据点的窗口
            threshold_percentage=Decimal("1.0")  # 1%波动阈值
        )
        self.last_price = None

    async def handle_price_update(self, price_data: PriceData):
        """处理价格更新"""
        self.price_count += 1
        
        print(f"价格更新 #{self.price_count}")
        print(f"   代币: {price_data.symbol}")
        print(f"   价格: {price_data.price} USDT")
        print(f"   成交量: {price_data.volume}")
        print(f"   时间: {price_data.timestamp}")
        
        # 计算价格变化
        if self.last_price:
            change = price_data.calculate_price_change(self.last_price)
            percentage = price_data.calculate_price_change_percentage(self.last_price)
            print(f"   变化: {change:+.6f} USDT ({percentage:+.2f}%)")
        
        # 检查波动
        is_volatile = self.monitor.add_price_data(price_data)
        if is_volatile:
            self.volatility_alerts += 1
            volatility_info = self.monitor.get_volatility_info()
            print(f"波动警报 #{self.volatility_alerts}")
            print(f"   波动率: {volatility_info['volatility_percentage']:.2f}%")
            print(f"   价格范围: {volatility_info['price_range']['min']:.6f} - {volatility_info['price_range']['max']:.6f}")
        
        self.last_price = price_data.price
        print()

    async def handle_connection_event(self, event_type: str, data: dict):
        """处理连接事件"""
        print(f"连接事件: {event_type}")
        if data:
            print(f"   数据: {data}")
        print()


async def test_price_websocket():
    """测试价格WebSocket连接"""
    print("测试价格WebSocket推送")
    print("=" * 60)
    
    # 创建测试处理器
    handler = PriceTestHandler()
    
    # 测试代币符号（使用小写格式）
    test_symbols = ["btcusdt", "ethusdt", "bnbusdt"]
    
    print(f"开始测试WebSocket连接")
    print(f"   测试代币: {test_symbols}")
    print(f"   波动阈值: 1.0%")
    print(f"   窗口大小: 10个数据点")
    print()
    
    # 为每个代币创建连接器
    connectors = []
    
    for symbol in test_symbols:
        print(f"创建 {symbol} 连接器...")
        connector = PriceWebSocketConnector(
            symbol=symbol,
            on_price_update=handler.handle_price_update,
            on_connection_event=handler.handle_connection_event,
        )
        connectors.append(connector)
    
    try:
        # 启动所有连接器
        print("启动所有连接器...")
        tasks = []
        for connector in connectors:
            task = asyncio.create_task(connector.start())
            tasks.append(task)
        
        # 等待一段时间接收数据
        print("等待价格数据...")
        await asyncio.sleep(30)  # 等待30秒
        
        print("测试统计:")
        print(f"   接收价格更新: {handler.price_count} 次")
        print(f"   波动警报: {handler.volatility_alerts} 次")
        print(f"   监控器状态: {handler.monitor}")
        
    except KeyboardInterrupt:
        print("\n用户中断测试")
    except Exception as e:
        print(f"测试出错: {e}")
    finally:
        # 停止所有连接器
        print("停止所有连接器...")
        for connector in connectors:
            await connector.stop()
        
        print("测试完成")


async def test_volatility_monitor():
    """测试波动监控器"""
    print("\n测试波动监控器")
    print("=" * 40)
    
    monitor = PriceVolatilityMonitor(
        window_size=5,
        threshold_percentage=Decimal("2.0")
    )
    
    # 模拟价格数据
    base_price = Decimal("100.0")
    test_prices = [
        Decimal("100.0"),
        Decimal("101.0"),
        Decimal("102.0"),
        Decimal("103.0"),
        Decimal("104.0"),  # 4%波动，应该触发警报
        Decimal("105.0"),
    ]
    
    print(f"模拟价格数据: {test_prices}")
    print(f"   阈值: 2.0%")
    print()
    
    for i, price_value in enumerate(test_prices):
        from binance.domain.value_objects.price import Price
        
        price_data = PriceData(
            symbol="test",
            price=Price(price_value, precision=8),
            volume=Decimal("100.0"),
            timestamp=datetime.now(),
        )
        
        is_volatile = monitor.add_price_data(price_data)
        volatility_info = monitor.get_volatility_info()
        
        print(f"价格 {i+1}: {price_value} USDT")
        print(f"   波动率: {volatility_info['volatility_percentage']:.2f}%")
        print(f"   是否波动: {'是' if is_volatile else '否'}")
        print()


if __name__ == "__main__":
    print("开始价格推送测试")
    print()
    
    # 测试波动监控器
    asyncio.run(test_volatility_monitor())
    
    # 测试WebSocket连接
    print("注意: WebSocket测试需要网络连接")
    print("   如果连接失败，请检查网络或币安API状态")
    print()
    
    try:
        asyncio.run(test_price_websocket())
    except Exception as e:
        print(f"WebSocket测试失败: {e}")
        print("   这可能是正常的，因为需要真实的网络连接")
