"""
API使用示例

演示如何使用API进行交易操作。
"""

import asyncio
import aiohttp
import json
from datetime import datetime


async def main():
    """主函数"""
    base_url = "http://localhost:8000/api/v1"
    
    async with aiohttp.ClientSession() as session:
        try:
            # 1. 健康检查
            print("1. 健康检查")
            async with session.get(f"{base_url}/health") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API状态: {data['status']}")
                else:
                    print(f"API健康检查失败: {response.status}")
                    return
            
            # 2. 获取API信息
            print("\n2. 获取API信息")
            async with session.get(f"{base_url}/info") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"API名称: {data['name']}")
                    print(f"版本: {data['version']}")
                    print(f"描述: {data['description']}")
                else:
                    print(f"获取API信息失败: {response.status}")
            
            # 3. 获取钱包余额 (需要替换为实际的用户ID)
            user_id = "1"  # 替换为实际的用户ID
            print(f"\n3. 获取用户 {user_id} 的钱包余额")
            async with session.get(f"{base_url}/wallet/{user_id}/balance") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"总估值: {data['total_valuation']} USDT")
                    print("资产列表:")
                    for asset in data['assets']:
                        print(f"  {asset['symbol']}: {asset['available_balance']} (估值: {asset['valuation']} USDT)")
                elif response.status == 404:
                    print("钱包不存在")
                else:
                    print(f"获取钱包余额失败: {response.status}")
            
            # 4. 获取订单列表
            print(f"\n4. 获取用户 {user_id} 的订单列表")
            async with session.get(f"{base_url}/orders?user_id={user_id}&limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        print("最近的订单:")
                        for order in data:
                            print(f"  {order['order_id']}: {order['symbol']} {order['side']} {order['quantity']} @ {order['price']} ({order['status']})")
                    else:
                        print("没有找到订单")
                else:
                    print(f"获取订单列表失败: {response.status}")
            
            # 5. 获取活跃订单
            print(f"\n5. 获取用户 {user_id} 的活跃订单")
            async with session.get(f"{base_url}/orders/active?user_id={user_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        print("活跃订单:")
                        for order in data:
                            print(f"  {order['order_id']}: {order['symbol']} {order['side']} {order['quantity']} @ {order['price']} ({order['status']})")
                    else:
                        print("没有活跃订单")
                else:
                    print(f"获取活跃订单失败: {response.status}")
            
            # 6. 获取交易历史
            print(f"\n6. 获取用户 {user_id} 的交易历史")
            async with session.get(f"{base_url}/trades?user_id={user_id}&limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        print("最近的交易:")
                        for trade in data:
                            print(f"  {trade['trade_id']}: {trade['symbol']} {trade['side']} {trade['quantity']} @ {trade['price']} ({trade['executed_at']})")
                    else:
                        print("没有找到交易记录")
                else:
                    print(f"获取交易历史失败: {response.status}")
            
            # 7. 获取交易量
            print(f"\n7. 获取用户 {user_id} 的24小时交易量")
            async with session.get(f"{base_url}/trades/volume?user_id={user_id}") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"总交易量: {data['total_volume']} USDT")
                    if data['volume_by_symbol']:
                        print("按交易对分类:")
                        for symbol, volume in data['volume_by_symbol'].items():
                            print(f"  {symbol}: {volume} USDT")
                else:
                    print(f"获取交易量失败: {response.status}")
            
            # 8. 获取投资组合摘要
            print(f"\n8. 获取用户 {user_id} 的投资组合摘要")
            async with session.get(f"{base_url}/portfolio/{user_id}/summary") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"总市值: {data['total_market_value']} USDT")
                    print(f"总盈亏: {data['total_pnl']} USDT")
                    print(f"盈亏百分比: {data['pnl_percentage']}%")
                    print(f"持仓数量: {data['position_count']}")
                else:
                    print(f"获取投资组合摘要失败: {response.status}")
            
            # 9. 获取持仓列表
            print(f"\n9. 获取用户 {user_id} 的持仓列表")
            async with session.get(f"{base_url}/portfolio/{user_id}/positions?limit=5") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        print("持仓列表:")
                        for position in data:
                            print(f"  {position['symbol']}: {position['quantity']} @ {position['avg_price']} (市值: {position['market_value']} USDT)")
                    else:
                        print("没有找到持仓")
                else:
                    print(f"获取持仓列表失败: {response.status}")
            
            # 10. 获取资产配置
            print(f"\n10. 获取用户 {user_id} 的资产配置")
            async with session.get(f"{base_url}/portfolio/{user_id}/allocation") as response:
                if response.status == 200:
                    data = await response.json()
                    if data:
                        print("资产配置:")
                        for symbol, percentage in data.items():
                            print(f"  {symbol}: {percentage}%")
                    else:
                        print("没有找到资产配置")
                else:
                    print(f"获取资产配置失败: {response.status}")
            
            # 11. 获取盈亏分析
            print(f"\n11. 获取用户 {user_id} 的盈亏分析")
            async with session.get(f"{base_url}/portfolio/{user_id}/pnl") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"总市值: {data['total_market_value']} USDT")
                    print(f"总未实现盈亏: {data['total_unrealized_pnl']} USDT")
                    print(f"总已实现盈亏: {data['total_realized_pnl']} USDT")
                    print(f"总盈亏: {data['total_pnl']} USDT")
                    print(f"盈亏百分比: {data['pnl_percentage']}%")
                    print(f"持仓数量: {data['position_count']}")
                    print(f"盈利持仓: {data['winning_positions']}")
                    print(f"亏损持仓: {data['losing_positions']}")
                    print(f"盈亏平衡持仓: {data['break_even_positions']}")
                else:
                    print(f"获取盈亏分析失败: {response.status}")
            
            # 12. 获取风险指标
            print(f"\n12. 获取用户 {user_id} 的风险指标")
            async with session.get(f"{base_url}/portfolio/{user_id}/risk") as response:
                if response.status == 200:
                    data = await response.json()
                    print(f"最大集中度: {data['max_concentration']}%")
                    print(f"持仓数量: {data['position_count']}")
                    print(f"平均持仓大小: {data['avg_position_size']} USDT")
                    print(f"多样化评分: {data['diversification_score']}")
                    print(f"风险等级: {data['risk_level']}")
                else:
                    print(f"获取风险指标失败: {response.status}")
            
        except Exception as e:
            print(f"API调用失败: {e}")


if __name__ == "__main__":
    asyncio.run(main())
