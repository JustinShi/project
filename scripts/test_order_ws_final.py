#!/usr/bin/env python3
"""测试订单 WebSocket 推送 - 最终版本"""

import asyncio
import json
import signal
from typing import Dict, Any

from binance.infrastructure.database.session import get_db
from binance.infrastructure.database.repositories.user_repository_impl import UserRepositoryImpl
from binance.infrastructure.binance_client.listen_key_manager import ListenKeyManager
from binance.infrastructure.binance_client.order_websocket import OrderWebSocketConnector
from binance.infrastructure.logging.logger import get_logger

logger = get_logger(__name__)

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


def _parse_cookies(raw: str) -> str:
    """解析cookies字符串"""
    return raw if raw else ""


async def _fetch_credentials(user_id: int) -> tuple[Dict[str, str], str]:
    """从数据库获取用户凭证"""
    async for session in get_db():
        repo = UserRepositoryImpl(session)
        user = await repo.get_by_id(user_id)
        
        if not user:
            raise RuntimeError(f"未找到用户 {user_id}")
        
        if not user.has_credentials():
            raise RuntimeError(f"用户 {user_id} 没有配置凭证")
        
        try:
            headers = json.loads(user.headers) if user.headers else {}
        except Exception:
            headers = {}
        
        cookies = _parse_cookies(user.cookies)
        return headers, cookies
    
    raise RuntimeError("数据库会话未返回凭证")


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
            print("\n" + "=" * 80)
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
                
                if order_data.get('commission'):
                    print(f"   手续费: {order_data.get('commission')} {order_data.get('commission_asset')}")
            
            print("=" * 80)
            
        except Exception as e:
            logger.error(f"处理订单更新异常: {e}")
    
    async def handle_connection_event(self, event_type: str, data: Dict[str, Any]):
        """处理连接事件"""
        self.connection_events.append({
            "event_type": event_type,
            "data": data
        })
        
        print(f"\n🔌 连接事件: {event_type}")
        if data:
            print(f"   {json.dumps(data, ensure_ascii=False)}")
    
    def print_statistics(self):
        """打印统计信息"""
        print("\n" + "=" * 80)
        print("📊 测试统计")
        print("=" * 80)
        print(f"总订单更新数: {len(self.order_updates)}")
        print(f"连接事件数: {len(self.connection_events)}")
        
        if self.order_count_by_status:
            print("\n订单状态分布:")
            for status, count in sorted(self.order_count_by_status.items()):
                print(f"   {status}: {count}")
        
        print("=" * 80)


async def test_order_websocket(user_id: int = 1, test_duration: int = 60):
    """测试订单 WebSocket 连接"""
    global _shutdown
    
    print("\n" + "=" * 80)
    print("🚀 测试订单 WebSocket 推送")
    print("=" * 80)
    print(f"用户ID: {user_id}")
    print(f"测试时长: {test_duration} 秒")
    print()
    
    # 创建测试处理器
    handler = OrderTestHandler()
    
    # 获取用户凭证
    try:
        logger.info(f"获取用户 {user_id} 的凭证...")
        headers, cookies = await _fetch_credentials(user_id)
        logger.info("用户凭证获取成功")
        print(f"✅ 用户凭证获取成功")
    except Exception as e:
        logger.error(f"获取用户凭证失败: {e}")
        print(f"❌ 获取用户凭证失败: {e}")
        return
    
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
            print(f"❌ 获取 ListenKey 失败: {message}")
            return
        
        logger.info(f"ListenKey 获取成功: {listen_key[:20]}...")
        print(f"✅ ListenKey 获取成功")
        print(f"   ListenKey: {listen_key[:30]}...")
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
        
        print(f"✅ WebSocket 连接器创建成功")
        
        # 启动连接（在后台任务中运行）
        logger.info("启动订单 WebSocket 连接...")
        connection_task = asyncio.create_task(order_connector.start())
        
        # 等待连接建立
        await asyncio.sleep(3)
        
        if order_connector.is_connected():
            print(f"✅ WebSocket 连接已建立")
        else:
            print(f"⚠️  WebSocket 连接未建立（可能正在连接中）")
        
        # 打印连接信息
        conn_info = order_connector.get_connection_info()
        print("\n📊 连接信息:")
        print(f"   用户ID: {conn_info['user_id']}")
        print(f"   已连接: {conn_info['connected']}")
        print(f"   重连尝试: {conn_info['reconnect_attempts']}/{conn_info['max_reconnect_attempts']}")
        
        print("\n💡 提示:")
        print("   - 请使用 quick_start_strategy.py 脚本触发订单")
        print("   - 或在币安 Alpha 平台手动下单")
        print("   - 按 Ctrl+C 停止测试")
        print()
        
        # 等待接收订单更新
        print(f"⏳ 等待订单更新（{test_duration} 秒）...\n")
        
        for i in range(test_duration):
            if _shutdown:
                print("\n⚠️  用户中断测试")
                break
            
            await asyncio.sleep(1)
            
            # 每10秒打印一次状态
            if (i + 1) % 10 == 0:
                if order_connector.is_connected():
                    print(f"⏱️  已运行 {i + 1}/{test_duration} 秒，接收到 {len(handler.order_updates)} 个订单更新")
                else:
                    print(f"⚠️  WebSocket 连接已断开 (运行了 {i + 1} 秒)")
                    break
        
    except KeyboardInterrupt:
        logger.info("用户中断测试")
        print("\n⚠️  用户中断测试")
    except Exception as e:
        logger.error(f"测试出错: {e}", exc_info=True)
        print(f"\n❌ 测试出错: {e}")
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
    parser.add_argument("--duration", type=int, default=60, help="测试时长（秒，默认: 60）")
    
    args = parser.parse_args()
    
    logger.info(f"开始订单 WebSocket 测试 (用户ID: {args.user}, 时长: {args.duration}秒)")
    
    try:
        asyncio.run(test_order_websocket(args.user, args.duration))
    except KeyboardInterrupt:
        logger.info("用户中断测试")
    except Exception as e:
        logger.error(f"测试失败: {e}", exc_info=True)
    finally:
        logger.info("测试结束")

