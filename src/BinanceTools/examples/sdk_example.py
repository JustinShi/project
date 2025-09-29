"""
SDK使用示例

演示如何使用SDK进行交易操作。
"""

import asyncio
from decimal import Decimal
from datetime import datetime

from ..interfaces.sdk.sdk_client import SdkClient
from ..interfaces.sdk.sdk_config import SdkConfig


async def main():
    """主函数"""
    # 创建SDK配置
    config = SdkConfig()
    
    # 检查配置
    if not config.validate_config():
        print("配置验证失败，请检查配置文件")
        return
    
    # 创建SDK客户端
    async with SdkClient(config) as client:
        print("SDK客户端已初始化")
        
        # 获取用户列表
        user_config = config.get_user_config()
        users = user_config.get_active_users()
        
        if not users:
            print("没有找到活跃用户")
            return
        
        # 使用第一个用户
        user = users[0]
        user_id = user["id"]
        print(f"使用用户: {user['name']} (ID: {user_id})")
        
        try:
            # 1. 获取钱包余额
            print("\n1. 获取钱包余额")
            wallet = await client.get_wallet_balance(user_id)
            if wallet:
                print(f"总估值: {wallet.total_valuation} USDT")
                print("资产列表:")
                for asset in wallet.assets:
                    print(f"  {asset.symbol}: {asset.available_balance} (估值: {asset.valuation} USDT)")
            else:
                print("钱包不存在")
            
            # 2. 获取订单历史
            print("\n2. 获取订单历史")
            orders = await client.get_order_history(user_id, limit=5)
            if orders:
                print("最近的订单:")
                for order in orders:
                    print(f"  {order.order_id}: {order.symbol} {order.side} {order.quantity} @ {order.price} ({order.status})")
            else:
                print("没有找到订单")
            
            # 3. 获取交易历史
            print("\n3. 获取交易历史")
            trades = await client.get_trade_history(user_id, limit=5)
            if trades:
                print("最近的交易:")
                for trade in trades:
                    print(f"  {trade.trade_id}: {trade.symbol} {trade.side} {trade.quantity} @ {trade.price} ({trade.executed_at})")
            else:
                print("没有找到交易记录")
            
            # 4. 获取交易量
            print("\n4. 获取24小时交易量")
            volume = await client.get_trading_volume(user_id)
            print(f"总交易量: {volume.total_volume} USDT")
            if volume.volume_by_symbol:
                print("按交易对分类:")
                for symbol, vol in volume.volume_by_symbol.items():
                    print(f"  {symbol}: {vol} USDT")
            
            # 5. 获取投资组合摘要
            print("\n5. 获取投资组合摘要")
            summary = await client.get_portfolio_summary(user_id)
            print(f"总市值: {summary['total_market_value']} USDT")
            print(f"总盈亏: {summary['total_pnl']} USDT")
            print(f"盈亏百分比: {summary['pnl_percentage']}%")
            print(f"持仓数量: {summary['position_count']}")
            
            # 6. 获取持仓列表
            print("\n6. 获取持仓列表")
            positions = await client.get_positions(user_id, limit=5)
            if positions:
                print("持仓列表:")
                for position in positions:
                    print(f"  {position.symbol}: {position.quantity} @ {position.avg_price} (市值: {position.market_value} USDT)")
            else:
                print("没有找到持仓")
            
            # 7. 获取资产配置
            print("\n7. 获取资产配置")
            allocation = await client.get_asset_allocation(user_id)
            if allocation:
                print("资产配置:")
                for symbol, percentage in allocation.items():
                    print(f"  {symbol}: {percentage}%")
            else:
                print("没有找到资产配置")
            
            # 8. 获取盈亏分析
            print("\n8. 获取盈亏分析")
            pnl = await client.get_pnl_analysis(user_id)
            print(f"总市值: {pnl['total_market_value']} USDT")
            print(f"总未实现盈亏: {pnl['total_unrealized_pnl']} USDT")
            print(f"总已实现盈亏: {pnl['total_realized_pnl']} USDT")
            print(f"总盈亏: {pnl['total_pnl']} USDT")
            print(f"盈亏百分比: {pnl['pnl_percentage']}%")
            print(f"持仓数量: {pnl['position_count']}")
            print(f"盈利持仓: {pnl['winning_positions']}")
            print(f"亏损持仓: {pnl['losing_positions']}")
            print(f"盈亏平衡持仓: {pnl['break_even_positions']}")
            
            # 9. 获取风险指标
            print("\n9. 获取风险指标")
            risk = await client.get_risk_metrics(user_id)
            print(f"最大集中度: {risk['max_concentration']}%")
            print(f"持仓数量: {risk['position_count']}")
            print(f"平均持仓大小: {risk['avg_position_size']} USDT")
            print(f"多样化评分: {risk['diversification_score']}")
            print(f"风险等级: {risk['risk_level']}")
            
        except Exception as e:
            print(f"操作失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
