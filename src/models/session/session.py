'''
【Model 层】登录会话表 sessions

作用
    记录"谁在什么时候登录过、这次登录现在还算不算数"。
    一行 = 一次登录（可以理解为一台设备）。

和 token 的关系
    refresh token 的 payload 里有 jti 字段，它的值 = 这里的 id。
    服务器拿到 refresh token → 取出 jti → 按 id 找到这一行 → 判断还能不能刷新。
    access token 和这张表无关。

谁会用它
    只有 repositories/session/session.py 直接读写这张表。
'''
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class SessionModel(Base):
    __tablename__ = 'sessions'

    # 会话 id（uuid 十六进制串），同时作为 refresh token 的 jti
    id: Mapped[str] = mapped_column(String(32), primary_key=True)
    # 属于哪个用户
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    # 只存 refresh token 的哈希，不存原文；数据库泄露也拿不到可用的 token（和密码同理）
    refresh_token_hash: Mapped[str] = mapped_column(String(64))
    # 会话到期时间，与 refresh token 的 exp 相同
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    # 作废时间：NULL = 仍有效；有值 = 已退出 / 已刷新换新 / 被强制下线
    revoked_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    # 创建（登录）时间
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
