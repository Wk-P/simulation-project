from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


# 用户表结构，只描述数据，不包含任何数据库操作
class UserModel(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    username: Mapped[str] = mapped_column(String(20), unique=True, index=True)
    password_hash: Mapped[str] = mapped_column(String(255))
    email: Mapped[str | None] = mapped_column(String(255), default=None)
    admin: Mapped[bool] = mapped_column(default=False)
    staff: Mapped[bool] = mapped_column(default=False)
    active: Mapped[bool] = mapped_column(default=True)
