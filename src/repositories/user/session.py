from datetime import datetime

from sqlalchemy import update
from sqlalchemy.orm import Session as ORMSession

from src.models.user.session import SessionModel


# 会话表的数据库读写，只负责存取；会话是否有效由 service 判断
class SessionRepository:
    def __init__(self, db: ORMSession):
        self.db = db

    def get_by_id(self, session_id: str) -> SessionModel | None:
        return self.db.get(SessionModel, session_id)

    def create(self, session: SessionModel) -> SessionModel:
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        return session

    def revoke(self, session: SessionModel, revoked_at: datetime) -> None:
        session.revoked_at = revoked_at
        self.db.commit()

    # 撤销某用户所有仍有效的会话（检测到 refresh token 被盗用时使用）
    def revoke_all_by_user(self, user_id: int, revoked_at: datetime) -> None:
        stmt = (
            update(SessionModel)
            .where(SessionModel.user_id == user_id, SessionModel.revoked_at.is_(None))
            .values(revoked_at=revoked_at)
        )
        self.db.execute(stmt)
        self.db.commit()
