"""SQLAlchemy ORM 模型定义"""

from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    DateTime,
    ForeignKey,
    Index,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from binance.config.constants import OTOOrderPairStatus


class Base(DeclarativeBase):
    """ORM基类"""

    pass


class User(Base):
    """用户账户（包含认证信息）"""

    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    email: Mapped[str | None] = mapped_column(String(255))

    # 认证信息（明文存储）
    headers: Mapped[str | None] = mapped_column(Text)
    cookies: Mapped[str | None] = mapped_column(Text)
    is_valid: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    # 关系
    oto_order_pairs: Mapped[list["OTOOrderPair"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 2", name="users_name_check"),
        Index("idx_users_is_valid", "is_valid"),
    )


class OTOOrderPair(Base):
    """OTO订单对（买单+卖单）- 仅记录本地配置，订单状态由API查询"""

    __tablename__ = "oto_order_pairs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    user_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )

    # 币安订单ID（直接存储字符串）
    buy_order_id: Mapped[str | None] = mapped_column(String(100))
    sell_order_id: Mapped[str | None] = mapped_column(String(100))

    # 订单对状态
    status: Mapped[str] = mapped_column(String(20), nullable=False)

    # 价格和数量信息
    target_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    buy_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    sell_price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    quantity: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)

    # 交易符号
    token_symbol_short: Mapped[str] = mapped_column(String(20), nullable=False)

    # 时间戳
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True))

    # 关系
    user: Mapped["User"] = relationship(back_populates="oto_order_pairs")

    __table_args__ = (
        CheckConstraint(
            f"status IN ('{OTOOrderPairStatus.PENDING.value}', "
            f"'{OTOOrderPairStatus.BUY_FILLED.value}', "
            f"'{OTOOrderPairStatus.COMPLETED.value}', "
            f"'{OTOOrderPairStatus.CANCELLED.value}', "
            f"'{OTOOrderPairStatus.FAILED.value}')",
            name="chk_pair_status",
        ),
        CheckConstraint("quantity > 0", name="chk_pair_quantity"),
        Index("idx_pair_user_id", "user_id"),
        Index("idx_pair_status", "status"),
        Index("idx_pair_created", "created_at"),
    )


class PriceHistory(Base):
    """价格历史（用于波动监控）"""

    __tablename__ = "price_history"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    symbol: Mapped[str] = mapped_column(String(20), nullable=False)
    price: Mapped[Decimal] = mapped_column(Numeric(18, 8), nullable=False)
    timestamp: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), nullable=False, index=True
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    __table_args__ = (
        CheckConstraint("price > 0", name="chk_price_positive"),
        Index("idx_price_symbol_timestamp", "symbol", "timestamp"),
    )

