"""Remove unused timestamp fields from users table

Revision ID: 002
Revises: 001
Create Date: 2025-10-11

"""

from collections.abc import Sequence

import sqlalchemy as sa

from alembic import op


# revision identifiers, used by Alembic.
revision: str = "002"
down_revision: str | None = "001"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """删除 users 表中不使用的时间戳字段"""
    # SQLite 不支持直接删除列，需要重建表
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.drop_column("created_at")
        batch_op.drop_column("updated_at")
        batch_op.drop_column("last_verified_at")


def downgrade() -> None:
    """恢复删除的时间戳字段"""
    with op.batch_alter_table("users", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "created_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column(
                "updated_at",
                sa.DateTime(timezone=True),
                server_default=sa.text("CURRENT_TIMESTAMP"),
                nullable=False,
            )
        )
        batch_op.add_column(
            sa.Column("last_verified_at", sa.DateTime(timezone=True), nullable=True)
        )
