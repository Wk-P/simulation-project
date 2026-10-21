from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.user import UserModel


class UsernameAlreadyExistsError(Exception):
    pass


# 用户表的数据库读写，只负责存取，不包含业务规则
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists_by_username(self, username: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.username == username)
        return self.db.scalar(stmt) is not None

    def create(self, user: UserModel) -> UserModel:
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as e:
            # 并发注册时由数据库唯一约束兜底
            self.db.rollback()
            raise UsernameAlreadyExistsError(user.username) from e
        self.db.refresh(user)
        return user
