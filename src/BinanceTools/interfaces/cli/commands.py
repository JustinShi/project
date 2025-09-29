"""
CLI命令

命令行命令定义。
"""

import click
import asyncio
from typing import Optional
from datetime import datetime

from ...application.services.trading_application_service import TradingApplicationService
from ...application.services.portfolio_application_service import PortfolioApplicationService


class Commands:
    """CLI命令"""
    
    def __init__(
        self,
        trading_service: TradingApplicationService,
        portfolio_service: PortfolioApplicationService
    ):
        """初始化命令"""
        self.trading_service = trading_service
        self.portfolio_service = portfolio_service
    
    @click.group()
    def wallet(self):
        """钱包相关命令"""
        pass
    
    @wallet.command()
    @click.option('--user-id', required=True, help='用户ID')
    def balance(self, user_id: str):
        """获取钱包余额"""
        async def _get_balance():
            try:
                wallet = await self.trading_service.get_wallet_balance(user_id)
                if wallet:
                    click.echo(f"用户 {user_id} 的钱包余额:")
                    click.echo(f"总估值: {wallet.total_valuation} USDT")
                    click.echo("资产列表:")
                    for asset in wallet.assets:
                        click.echo(f"  {asset.symbol}: {asset.available_balance} (估值: {asset.valuation} USDT)")
                else:
                    click.echo(f"用户 {user_id} 的钱包不存在")
            except Exception as e:
                click.echo(f"获取钱包余额失败: {e}")
        
        asyncio.run(_get_balance())
    
    @click.group()
    def order(self):
        """订单相关命令"""
        pass
    
    @order.command()
    @click.option('--user-id', required=True, help='用户ID')
    @click.option('--symbol', required=True, help='交易对')
    @click.option('--side', required=True, type=click.Choice(['BUY', 'SELL']), help='订单方向')
    @click.option('--quantity', required=True, type=float, help='数量')
    @click.option('--price', required=True, type=float, help='价格')
    @click.option('--time-in-force', default='GTC', help='订单有效期')
    def place(self, user_id: str, symbol: str, side: str, quantity: float, price: float, time_in_force: str):
        """下单"""
        async def _place_order():
            try:
                if side == 'BUY':
                    order = await self.trading_service.place_buy_order(user_id, symbol, quantity, price, time_in_force)
                else:
                    order = await self.trading_service.place_sell_order(user_id, symbol, quantity, price, time_in_force)
                
                click.echo(f"订单创建成功:")
                click.echo(f"  订单ID: {order.order_id}")
                click.echo(f"  交易对: {order.symbol}")
                click.echo(f"  方向: {order.side}")
                click.echo(f"  数量: {order.quantity}")
                click.echo(f"  价格: {order.price}")
                click.echo(f"  状态: {order.status}")
            except Exception as e:
                click.echo(f"下单失败: {e}")
        
        asyncio.run(_place_order())
    
    @order.command()
    @click.option('--user-id', required=True, help='用户ID')
    @click.option('--order-id', required=True, type=int, help='订单ID')
    def cancel(self, user_id: str, order_id: int):
        """取消订单"""
        async def _cancel_order():
            try:
                order = await self.trading_service.cancel_order(user_id, order_id)
                if order:
                    click.echo(f"订单 {order_id} 取消成功")
                else:
                    click.echo(f"订单 {order_id} 不存在或无法取消")
            except Exception as e:
                click.echo(f"取消订单失败: {e}")
        
        asyncio.run(_cancel_order())
    
    @order.command()
    @click.option('--user-id', required=True, help='用户ID')
    @click.option('--symbol', help='交易对')
    @click.option('--limit', default=10, help='显示数量')
    def list(self, user_id: str, symbol: Optional[str], limit: int):
        """获取订单列表"""
        async def _list_orders():
            try:
                orders = await self.trading_service.get_order_history(user_id, symbol, limit=limit)
                if orders:
                    click.echo(f"用户 {user_id} 的订单列表:")
                    for order in orders:
                        click.echo(f"  {order.order_id}: {order.symbol} {order.side} {order.quantity} @ {order.price} ({order.status})")
                else:
                    click.echo("没有找到订单")
            except Exception as e:
                click.echo(f"获取订单列表失败: {e}")
        
        asyncio.run(_list_orders())
    
    @click.group()
    def trade(self):
        """交易相关命令"""
        pass
    
    @trade.command()
    @click.option('--user-id', required=True, help='用户ID')
    @click.option('--symbol', help='交易对')
    @click.option('--limit', default=10, help='显示数量')
    def history(self, user_id: str, symbol: Optional[str], limit: int):
        """获取交易历史"""
        async def _get_trade_history():
            try:
                trades = await self.trading_service.get_trade_history(user_id, symbol, limit=limit)
                if trades:
                    click.echo(f"用户 {user_id} 的交易历史:")
                    for trade in trades:
                        click.echo(f"  {trade.trade_id}: {trade.symbol} {trade.side} {trade.quantity} @ {trade.price} ({trade.executed_at})")
                else:
                    click.echo("没有找到交易记录")
            except Exception as e:
                click.echo(f"获取交易历史失败: {e}")
        
        asyncio.run(_get_trade_history())
    
    @trade.command()
    @click.option('--user-id', required=True, help='用户ID')
    def volume(self, user_id: str):
        """获取交易量"""
        async def _get_volume():
            try:
                volume = await self.trading_service.get_trading_volume(user_id)
                click.echo(f"用户 {user_id} 的24小时交易量:")
                click.echo(f"总交易量: {volume.total_volume} USDT")
                if volume.volume_by_symbol:
                    click.echo("按交易对分类:")
                    for symbol, vol in volume.volume_by_symbol.items():
                        click.echo(f"  {symbol}: {vol} USDT")
            except Exception as e:
                click.echo(f"获取交易量失败: {e}")
        
        asyncio.run(_get_volume())
    
    @click.group()
    def portfolio(self):
        """投资组合相关命令"""
        pass
    
    @portfolio.command()
    @click.option('--user-id', required=True, help='用户ID')
    def summary(self, user_id: str):
        """获取投资组合摘要"""
        async def _get_summary():
            try:
                summary = await self.portfolio_service.get_performance_summary(user_id)
                click.echo(f"用户 {user_id} 的投资组合摘要:")
                click.echo(f"总市值: {summary['total_market_value']} USDT")
                click.echo(f"总盈亏: {summary['total_pnl']} USDT")
                click.echo(f"盈亏百分比: {summary['pnl_percentage']}%")
                click.echo(f"持仓数量: {summary['position_count']}")
            except Exception as e:
                click.echo(f"获取投资组合摘要失败: {e}")
        
        asyncio.run(_get_summary())
    
    @portfolio.command()
    @click.option('--user-id', required=True, help='用户ID')
    @click.option('--limit', default=10, help='显示数量')
    def positions(self, user_id: str, limit: int):
        """获取持仓列表"""
        async def _get_positions():
            try:
                positions = await self.portfolio_service.get_top_positions(user_id, limit)
                if positions:
                    click.echo(f"用户 {user_id} 的持仓列表:")
                    for position in positions:
                        click.echo(f"  {position.symbol}: {position.quantity} @ {position.avg_price} (市值: {position.market_value} USDT)")
                else:
                    click.echo("没有找到持仓")
            except Exception as e:
                click.echo(f"获取持仓列表失败: {e}")
        
        asyncio.run(_get_positions())
    
    @click.group()
    def config(self):
        """配置相关命令"""
        pass
    
    @config.command()
    def show(self):
        """显示配置"""
        click.echo("当前配置:")
        click.echo("  用户配置文件: configs/binance/users.json")
        click.echo("  API配置文件: configs/binance/api_config.json")
        click.echo("  代理配置文件: configs/proxy.json")
    
    @config.command()
    @click.option('--user-id', required=True, help='用户ID')
    def user(self, user_id: str):
        """显示用户配置"""
        async def _show_user_config():
            try:
                # 这里应该显示用户配置
                click.echo(f"用户 {user_id} 的配置:")
                click.echo("  状态: 已启用")
                click.echo("  认证: 已配置")
            except Exception as e:
                click.echo(f"获取用户配置失败: {e}")
        
        asyncio.run(_show_user_config())
