from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


# 登录会话表，一行 = 一次登录（一台设备），refresh token 是否有效由这里决定
class SessionModel(Base):
    __tablename__ = 'sessions'

    # 会话 id，同时作为 refresh token 的 jti
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    # 只存 refresh token 的哈希，数据库泄露也拿不到可用的 token
    refresh_token_hash: Mapped[str] = mapped_column(String(64))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # NULL 表示会话仍有效
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
