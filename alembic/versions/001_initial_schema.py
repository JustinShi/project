"""Initial schema

Revision ID: 001
Revises:
Create Date: 2025-10-09

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "001"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    # 创建users表
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=100), nullable=False),
        sa.Column("display_name", sa.String(length=200), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("LENGTH(username) >= 3", name="users_username_check"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("idx_users_username", "users", ["username"])
    op.create_index("idx_users_is_active", "users", ["is_active"])

    # 创建auth_credentials表
    op.create_table(
        "auth_credentials",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("headers_encrypted", sa.Text(), nullable=False),
        sa.Column("cookies_encrypted", sa.Text(), nullable=False),
        sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("is_valid", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_auth_user_id", "auth_credentials", ["user_id"])

    # 创建trading_configs表
    op.create_table(
        "trading_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("token_symbol_short", sa.String(length=20), nullable=False),
        sa.Column("target_volume", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "current_volume",
            sa.Numeric(precision=18, scale=8),
            nullable=False,
            server_default="0",
        ),
        sa.Column("price_offset_mode", sa.String(length=20), nullable=False),
        sa.Column(
            "buy_offset_value", sa.Numeric(precision=18, scale=8), nullable=False
        ),
        sa.Column(
            "sell_offset_value", sa.Numeric(precision=18, scale=8), nullable=False
        ),
        sa.Column("order_quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "timeout_seconds", sa.Integer(), nullable=False, server_default="300"
        ),
        sa.Column(
            "price_volatility_threshold",
            sa.Numeric(precision=5, scale=2),
            nullable=False,
            server_default="2.0",
        ),
        sa.Column(
            "is_trading_active", sa.Boolean(), nullable=False, server_default="false"
        ),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint(
            "price_offset_mode IN ('PERCENTAGE', 'FIXED')", name="chk_offset_mode"
        ),
        sa.CheckConstraint("target_volume > 0", name="chk_target_volume"),
        sa.CheckConstraint("order_quantity > 0", name="chk_order_quantity"),
        sa.CheckConstraint("price_volatility_threshold >= 0", name="chk_volatility"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_config_user_id", "trading_configs", ["user_id"])
    op.create_index("idx_config_is_trading", "trading_configs", ["is_trading_active"])

    # 创建token_mappings表
    op.create_table(
        "token_mappings",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol_short", sa.String(length=20), nullable=False),
        sa.Column("token_name", sa.String(length=100), nullable=True),
        sa.Column("order_api_symbol", sa.String(length=50), nullable=False),
        sa.Column("websocket_symbol", sa.String(length=50), nullable=False),
        sa.Column("alpha_id", sa.String(length=50), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol_short"),
    )
    op.create_index("idx_token_symbol_short", "token_mappings", ["symbol_short"])
    op.create_index("idx_token_order_symbol", "token_mappings", ["order_api_symbol"])

    # 创建token_precisions表
    op.create_table(
        "token_precisions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol_short", sa.String(length=20), nullable=False),
        sa.Column("trade_decimal", sa.Integer(), nullable=False),
        sa.Column("token_decimal", sa.Integer(), nullable=False),
        sa.Column(
            "cached_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.CheckConstraint(
            "trade_decimal >= 0 AND trade_decimal <= 18", name="chk_trade_decimal"
        ),
        sa.CheckConstraint(
            "token_decimal >= 0 AND token_decimal <= 18", name="chk_token_decimal"
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("symbol_short"),
    )
    op.create_index("idx_precision_symbol", "token_precisions", ["symbol_short"])
    op.create_index("idx_precision_expires", "token_precisions", ["expires_at"])

    # 创建trading_statistics表
    op.create_table(
        "trading_statistics",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column(
            "total_volume_usdt",
            sa.Numeric(precision=18, scale=8),
            nullable=False,
            server_default="0",
        ),
        sa.Column("completed_cycles", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("total_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "successful_orders", sa.Integer(), nullable=False, server_default="0"
        ),
        sa.Column("failed_orders", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("last_trade_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("total_volume_usdt >= 0", name="chk_stats_volume"),
        sa.CheckConstraint("completed_cycles >= 0", name="chk_stats_cycles"),
        sa.CheckConstraint("total_orders >= 0", name="chk_stats_total"),
        sa.CheckConstraint("successful_orders >= 0", name="chk_stats_success"),
        sa.CheckConstraint("failed_orders >= 0", name="chk_stats_failed"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id"),
    )
    op.create_index("idx_stats_user_id", "trading_statistics", ["user_id"])

    # 创建orders表
    op.create_table(
        "orders",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("exchange_order_id", sa.String(length=100), nullable=True),
        sa.Column("token_symbol_short", sa.String(length=20), nullable=False),
        sa.Column("side", sa.String(length=10), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "filled_quantity",
            sa.Numeric(precision=18, scale=8),
            nullable=False,
            server_default="0",
        ),
        sa.Column("total_amount", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column(
            "filled_amount",
            sa.Numeric(precision=18, scale=8),
            nullable=False,
            server_default="0",
        ),
        sa.Column("submitted_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("side IN ('BUY', 'SELL')", name="chk_order_side"),
        sa.CheckConstraint(
            "status IN ('PENDING', 'SUBMITTED', 'PARTIALLY_FILLED', 'FILLED', 'CANCELLING', 'CANCELLED', 'FAILED', 'EXPIRED')",
            name="chk_order_status",
        ),
        sa.CheckConstraint("quantity > 0", name="chk_order_quantity"),
        sa.CheckConstraint("filled_quantity >= 0", name="chk_order_filled"),
        sa.CheckConstraint("filled_quantity <= quantity", name="chk_order_filled_lte"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_order_user_id", "orders", ["user_id"])
    op.create_index("idx_order_exchange_id", "orders", ["exchange_order_id"])
    op.create_index("idx_order_status", "orders", ["status"])
    op.create_index("idx_order_created", "orders", ["created_at"])

    # 创建oto_order_pairs表
    op.create_table(
        "oto_order_pairs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("buy_order_id", sa.Integer(), nullable=True),
        sa.Column("sell_order_id", sa.Integer(), nullable=True),
        sa.Column("status", sa.String(length=20), nullable=False),
        sa.Column("target_price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("buy_price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("sell_price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("token_symbol_short", sa.String(length=20), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "status IN ('PENDING', 'BUY_SUBMITTED', 'BUY_EXECUTING', 'BUY_COMPLETED', 'SELL_SUBMITTED', 'SELL_EXECUTING', 'COMPLETED', 'CANCELLED', 'FAILED')",
            name="chk_pair_status",
        ),
        sa.CheckConstraint("quantity > 0", name="chk_pair_quantity"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["buy_order_id"], ["orders.id"]),
        sa.ForeignKeyConstraint(["sell_order_id"], ["orders.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_pair_user_id", "oto_order_pairs", ["user_id"])
    op.create_index("idx_pair_status", "oto_order_pairs", ["status"])
    op.create_index("idx_pair_created", "oto_order_pairs", ["created_at"])

    # 创建trade_records表
    op.create_table(
        "trade_records",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("trade_id", sa.String(length=100), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("quantity", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("trade_time", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("quantity > 0", name="chk_trade_quantity"),
        sa.CheckConstraint("price > 0", name="chk_trade_price"),
        sa.ForeignKeyConstraint(["order_id"], ["orders.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("trade_id", "order_id", name="uq_trade_id_order"),
    )
    op.create_index("idx_trade_order_id", "trade_records", ["order_id"])
    op.create_index("idx_trade_time", "trade_records", ["trade_time"])

    # 创建price_history表
    op.create_table(
        "price_history",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("symbol", sa.String(length=20), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=8), nullable=False),
        sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.CheckConstraint("price > 0", name="chk_price_positive"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "idx_price_symbol_timestamp", "price_history", ["symbol", "timestamp"]
    )
    op.create_index(op.f("ix_price_history_timestamp"), "price_history", ["timestamp"])


def downgrade() -> None:
    # 删除所有表（按依赖关系逆序）
    op.drop_table("price_history")
    op.drop_table("trade_records")
    op.drop_table("oto_order_pairs")
    op.drop_table("orders")
    op.drop_table("trading_statistics")
    op.drop_table("token_precisions")
    op.drop_table("token_mappings")
    op.drop_table("trading_configs")
    op.drop_table("auth_credentials")
    op.drop_table("users")
