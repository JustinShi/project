"""SQLAlchemy ORM 模型定义"""

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Index,
    Integer,
    String,
    Text,
)
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


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

    __table_args__ = (
        CheckConstraint("LENGTH(name) >= 2", name="users_name_check"),
        Index("idx_users_is_valid", "is_valid"),
    )
