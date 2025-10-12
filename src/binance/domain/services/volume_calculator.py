"""交易量计算领域服务"""

from decimal import ROUND_UP, Decimal


class VolumeCalculator:
    """交易量计算领域服务

    负责计算交易循环次数
    """

    @staticmethod
    def calculate_required_cycles(
        target_volume: Decimal,
        current_volume: Decimal,
        single_order_amount: Decimal,
        multiplier: Decimal = Decimal("1"),
    ) -> int:
        """计算达到目标交易量所需的循环次数

        Args:
            target_volume: 目标交易量（USDT）
            current_volume: 当前已完成交易量（USDT，来自API查询）
            single_order_amount: 单次订单代币买入金额（USDT）
            multiplier: 交易积分倍数（如4倍积分币种为4，普通币种为1）

        Returns:
            所需循环次数

        Raises:
            ValueError: 参数无效时抛出
        """
        if target_volume <= 0:
            raise ValueError(f"目标交易量必须大于0: {target_volume}")

        if current_volume < 0:
            raise ValueError(f"当前交易量不能为负数: {current_volume}")

        if single_order_amount <= 0:
            raise ValueError(f"单次订单金额必须大于0: {single_order_amount}")

        if multiplier <= 0:
            raise ValueError(f"交易积分倍数必须大于0: {multiplier}")

        # 计算实际交易量（API查询的交易量需要除以倍数）
        actual_current_volume = current_volume / multiplier

        # 已达到目标
        if actual_current_volume >= target_volume:
            return 0

        # 计算剩余需要交易的量
        remaining_volume = target_volume - actual_current_volume

        # 计算所需循环次数（向上取整）
        cycles = (remaining_volume / single_order_amount).to_integral_value(
            rounding=ROUND_UP
        )

        return int(cycles)

    @staticmethod
    def calculate_actual_volume(
        api_volume: Decimal, multiplier: Decimal = Decimal("1")
    ) -> Decimal:
        """计算实际交易量（考虑积分倍数）

        Args:
            api_volume: API查询的交易量
            multiplier: 交易积分倍数（如4倍积分币种为4，普通币种为1）

        Returns:
            实际交易量
        """
        if api_volume < 0:
            raise ValueError(f"API交易量不能为负数: {api_volume}")

        if multiplier <= 0:
            raise ValueError(f"交易积分倍数必须大于0: {multiplier}")

        return api_volume / multiplier

    @staticmethod
    def calculate_remaining_volume(
        target_volume: Decimal,
        current_volume: Decimal,
        multiplier: Decimal = Decimal("1"),
    ) -> Decimal:
        """计算剩余需要交易的量

        Args:
            target_volume: 目标交易量
            current_volume: 当前已完成交易量（API查询值）
            multiplier: 交易积分倍数

        Returns:
            剩余交易量
        """
        actual_current_volume = VolumeCalculator.calculate_actual_volume(
            current_volume, multiplier
        )

        if actual_current_volume >= target_volume:
            return Decimal("0")

        return target_volume - actual_current_volume

    @staticmethod
    def calculate_progress_percentage(
        target_volume: Decimal,
        current_volume: Decimal,
        multiplier: Decimal = Decimal("1"),
    ) -> Decimal:
        """计算交易进度百分比

        Args:
            target_volume: 目标交易量
            current_volume: 当前已完成交易量（API查询值）
            multiplier: 交易积分倍数

        Returns:
            进度百分比（0-100）
        """
        if target_volume <= 0:
            return Decimal("0")

        actual_current_volume = VolumeCalculator.calculate_actual_volume(
            current_volume, multiplier
        )
        progress = (actual_current_volume / target_volume) * Decimal("100")

        # 限制在0-100之间
        if progress < 0:
            return Decimal("0")
        elif progress > 100:
            return Decimal("100")

        return progress
