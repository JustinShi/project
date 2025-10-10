#!/usr/bin/env python3
"""测试订单 WebSocket 推送"""

import asyncio
import json
import logging
import sys
import signal
from pathlib import Path
from typing import Dict, Any

# 添加项目路径到 sys.path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root / "src"))

from binance.infrastructure.binance_client.order_websocket import OrderWebSocketConnector
from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.database.db_connection import Database
from binance.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl

# 设置日志
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# 全局停止标志
_shutdown = False


def signal_handler(signum, frame):
    """信号处理器"""
    global _shutdown
    logger.info(f"收到信号 {signum}，准备停止...")
    _shutdown = True


# 注册信号处理器
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


class OrderTestHandler:
    """订单测试处理器"""
    
    def __init__(self):
        self.order_updates = []
        self.connection_events = []
        self.order_count_by_status = {}
    
    async def handle_order_update(self, order_data: Dict[str, Any]):
        """处理订单更新"""
        try:
            self.order_updates.append(order_data)
            
            # 统计订单状态
            status = order_data.get("status", "UNKNOWN")
            self.order_count_by_status[status] = self.order_count_by_status.get(status, 0) + 1
            
            # 打印订单信息
            print("=" * 80)
            print(f"📦 订单更新 #{len(self.order_updates)}")
            print("-" * 80)
            
            if order_data.get("event_type") == "account_update":
                print(f"账户更新:")
                print(f"   用户ID: {order_data.get('user_id')}")
                print(f"   余额: {order_data.get('balances', [])}")
            else:
                print(f"订单信息:")
                print(f"   用户ID: {order_data.get('user_id')}")
                print(f"   订单ID: {order_data.get('order_id')}")
                print(f"   客户端订单ID: {order_data.get('client_order_id')}")
                print(f"   交易对: {order_data.get('symbol')}")
                print(f"   方向: {order_data.get('side')}")
                print(f"   类型: {order_data.get('type')}")
                print(f"   状态: {order_data.get('status')}")
                print(f"   价格: {order_data.get('price')}")
                print(f"   数量: {order_data.get('quantity')}")
                print(f"   已执行: {order_data.get('executed_quantity')}")
                print(f"   执行类型: {order_data.get('execution_type')}")
                
                if order_data.get('order_reject_reason'):
                    print(f"   拒绝原因: {order_data.get('order_reject_reason')}")
                
                if order_data.get('commission'):
                    print(f"   手续费: {order_data.get('commission')} {order_data.get('commission_asset')}")
            
            print("=" * 80)
            print()
            
        except Exception as e:
            logger.error(f"处理订单更新异常: {e}")
    
    async def handle_connection_event(self, event_type: str, data: Dict[str, Any]):
        """处理连接事件"""
        self.connection_events.append({
            "event_type": event_type,
            "data": data
        })
        
        print("🔌 连接事件:")
        print(f"   事件类型: {event_type}")
        if data:
            print(f"   数据: {json.dumps(data, indent=2, ensure_ascii=False)}")
        print()
    
    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("📊 测试统计")
        print("=" * 80)
        print(f"总订单更新数: {len(self.order_updates)}")
        print(f"连接事件数: {len(self.connection_events)}")
        print()
        
        if self.order_count_by_status:
            print("订单状态分布:")
            for status, count in sorted(self.order_count_by_status.items()):
                print(f"   {status}: {count}")
        
        print("=" * 80)


async def get_user_credentials(user_id: int):
    """从数据库获取用户凭证"""
    try:
        # 初始化数据库连接
        db = Database()
        
        # 创建用户仓储
        user_repo = UserRepositoryImpl(db)
        
        # 获取用户信息
        user = await user_repo.get_user_by_id(user_id)
        
        if not user:
            logger.error(f"用户 {user_id} 不存在")
            return None, None
        
        if not user.credentials:
            logger.error(f"用户 {user_id} 没有配置凭证")
            return None, None
        
        logger.info(f"成功获取用户 {user_id} 的凭证")
        return user.credentials.headers, user.credentials.cookies
        
    except Exception as e:
        logger.error(f"获取用户凭证失败: {e}")
        return None, None


async def test_order_websocket(user_id: int = 1):
    """测试订单 WebSocket 连接"""
    global _shutdown
    
    print("\n" + "=" * 80)
    print("🚀 测试订单 WebSocket 推送")
    print("=" * 80)
    print(f"用户ID: {user_id}")
    print()
    
    # 创建测试处理器
    handler = OrderTestHandler()
    
    # 获取用户凭证
    logger.info(f"获取用户 {user_id} 的凭证...")
    headers, cookies = await get_user_credentials(user_id)
    
    if not headers or not cookies:
        logger.error("无法获取用户凭证，测试终止")
        return
    
    logger.info("用户凭证获取成功")
    
    # 创建 ListenKey 管理器
    listen_key_manager = None
    order_connector = None
    
    try:
        logger.info("创建 ListenKey 管理器...")
        listen_key_manager = ListenKeyManager(headers, cookies)
        
        # 获取 ListenKey
        logger.info("获取 ListenKey...")
        success, message, listen_key = await listen_key_manager.get_listen_key()
        
        if not success or not listen_key:
            logger.error(f"获取 ListenKey 失败: {message}")
            return
        
        logger.info(f"ListenKey 获取成功: {listen_key[:20]}...")
        print(f"✅ ListenKey 获取成功")
        print()
        
        # 创建订单 WebSocket 连接器
        logger.info("创建订单 WebSocket 连接器...")
        order_connector = OrderWebSocketConnector(
            user_id=user_id,
            listen_key=listen_key,
            on_order_update=handler.handle_order_update,
            on_connection_event=handler.handle_connection_event,
            reconnect_interval=3,
            max_reconnect_attempts=10
        )
        
        print(f"✅ 订单 WebSocket 连接器创建成功")
        print()
        
        # 启动连接（在后台任务中运行）
        logger.info("启动订单 WebSocket 连接...")
        connection_task = asyncio.create_task(order_connector.start())
        
        # 等待连接建立
        await asyncio.sleep(2)
        
        if order_connector.is_connected():
            print(f"✅ WebSocket 连接已建立")
            print()
        else:
            print(f"⚠️  WebSocket 连接未建立（可能正在连接中）")
            print()
        
        # 打印连接信息
        conn_info = order_connector.get_connection_info()
        print("连接信息:")
        print(f"   用户ID: {conn_info['user_id']}")
        print(f"   ListenKey: {conn_info['listen_key'][:20]}...")
        print(f"   已连接: {conn_info['connected']}")
        print(f"   重连尝试: {conn_info['reconnect_attempts']}/{conn_info['max_reconnect_attempts']}")
        print()
        
        print("💡 提示:")
        print("   - 请在币安 Alpha 平台下单，观察 WebSocket 推送")
        print("   - 或者使用 quick_start_strategy.py 脚本触发订单")
        print("   - 按 Ctrl+C 停止测试")
        print()
        
        # 等待接收订单更新
        print("⏳ 等待订单更新...")
        print()
        
        # 持续运行直到收到停止信号
        check_count = 0
        while not _shutdown:
            await asyncio.sleep(1)
            check_count += 1
            
            # 每10秒检查一次连接状态
            if check_count % 10 == 0:
                if order_connector.is_connected():
                    logger.debug(f"WebSocket 连接正常 (已运行 {check_count} 秒)")
                else:
                    logger.warning(f"WebSocket 连接已断开 (运行了 {check_count} 秒)")
            
            # 每30秒打印一次统计
            if check_count % 30 == 0:
                print(f"⏱️  已运行 {check_count} 秒，接收到 {len(handler.order_updates)} 个订单更新")
        
    except KeyboardInterrupt:
        logger.info("用户中断测试")
    except Exception as e:
        logger.error(f"测试出错: {e}", exc_info=True)
    finally:
        # 停止订单 WebSocket 连接
        if order_connector:
            logger.info("停止订单 WebSocket 连接...")
            await order_connector.stop()
        
        # 关闭 ListenKey 管理器
        if listen_key_manager:
            logger.info("关闭 ListenKey 管理器...")
            await listen_key_manager.close()
        
        # 打印统计信息
        handler.print_statistics()
        
        print("\n✅ 测试完成")


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="测试订单 WebSocket 推送")
    parser.add_argument("--user", type=int, default=1, help="用户ID（默认: 1）")
    
    args = parser.parse_args()
    
    logger.info(f"开始订单 WebSocket 测试 (用户ID: {args.user})")
    
    try:
        asyncio.run(test_order_websocket(args.user))
    except KeyboardInterrupt:
        logger.info("用户中断测试")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
    finally:
        logger.info("测试结束")

