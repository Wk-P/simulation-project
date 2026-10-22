'''
【Repository 层】sessions 表的读写

作用
    只负责"查、写、改"，不做任何判断。
    例如：会话过没过期、能不能刷新 —— 这些判断在 services/session/session.py 里。

谁调用它
    services/session/session.py（start_session / refresh_session / end_session）

它调用谁
    SQLAlchemy 的 db session（由 routers/deps.py 的 get_session_repo 注入）
'''
from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session as ORMSession

from src.models.session.session import SessionModel


class SessionRepository:
    # db 是本次 HTTP 请求的数据库连接，请求结束自动关闭
    def __init__(self, db: ORMSession):
        self.db = db

    # 按会话 id（= refresh token 的 jti）查一行，找不到返回 None
    def get_session_by_id(self, session_id: str) -> SessionModel | None:
        return self.db.get(SessionModel, session_id)

    # 新增一行会话（登录、刷新时调用）
    def create_session(self, session: SessionModel) -> SessionModel:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    # 作废一个会话：填上 revoked_at（退出、刷新换新时调用）
    def revoke_session(self, session: SessionModel, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at
        self.db.commit()

    # 作废某用户所有仍有效的会话（检测到 refresh token 被盗用时调用）
    def revoke_sessions_by_user_id(self, user_id: int, revoked_at: datetime) -> None:
        stmt = (
            update(SessionModel)
            .where(SessionModel.user_id == user_id, SessionModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        self.db.execute(stmt)
        self.db.commit()
