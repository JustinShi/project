"""
风险领域服务

处理风险控制相关的业务逻辑。
"""

from typing import List, Dict, Optional
from decimal import Decimal
from datetime import datetime, timedelta

from ..entities.order import Order
from ..entities.trade import Trade
from ..entities.wallet import Wallet
from ..value_objects.symbol import Symbol
from ..value_objects.money import Money


class RiskService:
    """风险领域服务"""
    
    def __init__(
        self,
        max_position_size: Decimal = Decimal('0.1'),  # 最大仓位比例 10%
        max_daily_loss: Decimal = Decimal('0.05'),    # 最大日亏损 5%
        max_daily_volume: Decimal = Decimal('10000'), # 最大日交易量
        min_liquidity: Decimal = Decimal('100000')    # 最小流动性
    ):
        """初始化风险服务"""
        self.max_position_size = max_position_size
        self.max_daily_loss = max_daily_loss
        self.max_daily_volume = max_daily_volume
        self.min_liquidity = min_liquidity
    
    def check_position_size_risk(
        self,
        wallet: Wallet,
        symbol: Symbol,
        order_quantity: Decimal,
        order_price: Decimal
    ) -> bool:
        """检查仓位大小风险"""
        # 计算订单价值
        order_value = order_quantity * order_price
        
        # 获取总资产价值
        total_value = wallet.total_valuation
        
        if total_value == 0:
            return False
        
        # 计算仓位比例
        position_ratio = order_value / total_value
        
        return position_ratio <= self.max_position_size
    
    def check_daily_loss_risk(
        self,
        trades: List[Trade],
        wallet: Wallet
    ) -> bool:
        """检查日亏损风险"""
        today = datetime.utcnow().date()
        today_trades = [
            trade for trade in trades
            if trade.executed_at.date() == today
        ]
        
        if not today_trades:
            return True
        
        # 计算今日盈亏
        total_pnl = Decimal('0')
        for trade in today_trades:
            # 这里简化计算，实际应该根据买卖配对计算
            if trade.is_sell_trade():
                total_pnl += trade.calculate_total_value()
            else:
                total_pnl -= trade.calculate_total_value()
        
        # 计算亏损比例
        if wallet.total_valuation > 0:
            loss_ratio = abs(min(total_pnl, 0)) / wallet.total_valuation
            return loss_ratio <= self.max_daily_loss
        
        return True
    
    def check_daily_volume_risk(
        self,
        trades: List[Trade]
    ) -> bool:
        """检查日交易量风险"""
        today = datetime.utcnow().date()
        today_trades = [
            trade for trade in trades
            if trade.executed_at.date() == today
        ]
        
        if not today_trades:
            return True
        
        # 计算今日交易量
        total_volume = sum(
            trade.calculate_total_value() for trade in today_trades
        )
        
        return total_volume <= self.max_daily_volume
    
    def check_liquidity_risk(
        self,
        symbol: Symbol,
        order_quantity: Decimal,
        market_liquidity: Decimal
    ) -> bool:
        """检查流动性风险"""
        if market_liquidity < self.min_liquidity:
            return False
        
        # 检查订单大小是否超过市场流动性的某个比例
        max_order_ratio = Decimal('0.01')  # 1%
        max_order_size = market_liquidity * max_order_ratio
        
        return order_quantity <= max_order_size
    
    def check_concentration_risk(
        self,
        wallet: Wallet,
        symbol: Symbol,
        max_concentration: Decimal = Decimal('0.3')  # 30%
    ) -> bool:
        """检查集中度风险"""
        # 获取指定代币的持仓
        asset = wallet.get_asset_by_symbol(symbol.base_asset)
        if not asset:
            return True
        
        # 计算该代币占总资产的比例
        if wallet.total_valuation > 0:
            concentration = asset.valuation / wallet.total_valuation
            return concentration <= max_concentration
        
        return True
    
    def check_volatility_risk(
        self,
        symbol: Symbol,
        price_history: List[Decimal],
        max_volatility: Decimal = Decimal('0.2')  # 20%
    ) -> bool:
        """检查波动性风险"""
        if len(price_history) < 2:
            return True
        
        # 计算价格变化率
        price_changes = []
        for i in range(1, len(price_history)):
            change = (price_history[i] - price_history[i-1]) / price_history[i-1]
            price_changes.append(abs(change))
        
        if not price_changes:
            return True
        
        # 计算平均波动率
        avg_volatility = sum(price_changes) / len(price_changes)
        
        return avg_volatility <= max_volatility
    
    def check_market_hours_risk(
        self,
        current_time: datetime = None
    ) -> bool:
        """检查交易时间风险"""
        if current_time is None:
            current_time = datetime.utcnow()
        
        # 检查是否在交易时间内（这里简化处理）
        # 实际应该根据具体交易所的交易时间来判断
        hour = current_time.hour
        
        # 假设交易时间为UTC 0-23点（24小时交易）
        return True
    
    def calculate_risk_score(
        self,
        wallet: Wallet,
        symbol: Symbol,
        order_quantity: Decimal,
        order_price: Decimal,
        trades: List[Trade],
        market_liquidity: Decimal = Decimal('1000000'),
        price_history: List[Decimal] = None
    ) -> Dict[str, any]:
        """计算综合风险评分"""
        risk_factors = {
            "position_size_risk": self.check_position_size_risk(
                wallet, symbol, order_quantity, order_price
            ),
            "daily_loss_risk": self.check_daily_loss_risk(trades, wallet),
            "daily_volume_risk": self.check_daily_volume_risk(trades),
            "liquidity_risk": self.check_liquidity_risk(
                symbol, order_quantity, market_liquidity
            ),
            "concentration_risk": self.check_concentration_risk(wallet, symbol),
            "market_hours_risk": self.check_market_hours_risk()
        }
        
        if price_history:
            risk_factors["volatility_risk"] = self.check_volatility_risk(
                symbol, price_history
            )
        
        # 计算风险评分（0-100，越低越安全）
        risk_score = 0
        for factor, passed in risk_factors.items():
            if not passed:
                risk_score += 20  # 每个风险因子失败增加20分
        
        risk_factors["overall_risk_score"] = risk_score
        risk_factors["risk_level"] = self._get_risk_level(risk_score)
        
        return risk_factors
    
    def _get_risk_level(self, risk_score: int) -> str:
        """获取风险等级"""
        if risk_score <= 20:
            return "LOW"
        elif risk_score <= 40:
            return "MEDIUM"
        elif risk_score <= 60:
            return "HIGH"
        else:
            return "CRITICAL"
    
    def should_reject_order(
        self,
        wallet: Wallet,
        symbol: Symbol,
        order_quantity: Decimal,
        order_price: Decimal,
        trades: List[Trade],
        market_liquidity: Decimal = Decimal('1000000'),
        price_history: List[Decimal] = None
    ) -> bool:
        """判断是否应该拒绝订单"""
        risk_factors = self.calculate_risk_score(
            wallet, symbol, order_quantity, order_price,
            trades, market_liquidity, price_history
        )
        
        # 如果风险评分超过60分，拒绝订单
        return risk_factors["overall_risk_score"] > 60
