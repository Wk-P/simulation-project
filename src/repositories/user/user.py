'''
【Repository 层】users 表的读写

作用
    只负责"查、写、改"，不做任何判断。
    例如：密码对不对、格式合不合规 —— 这些判断在 services/user/ 里。

谁调用它
    services/user/register.py、services/auth/、services/user/me.py

它调用谁
    SQLAlchemy 的 db session（由 routers/deps.py 的 get_user_repo 注入）
'''
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from src.models.user.user import UserModel


class UsernameAlreadyExistsError(Exception):
    pass


# 用户表的数据库读写，只负责存取，不包含业务规则
class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def exists_by_username(self, username: str) -> bool:
        stmt = select(UserModel.id).where(UserModel.username == username)
        return self.db.scalar(stmt) is not None

    def create_user(self, user: UserModel) -> UserModel:
        self.db.add(user)
        try:
            self.db.commit()
        except IntegrityError as e:
            # 并发注册时由数据库唯一约束兜底
            self.db.rollback()
            raise UsernameAlreadyExistsError(user.username) from e
        self.db.refresh(user)
        return user

    def get_user_by_id(self, user_id: int) -> UserModel | None:
        return self.db.get(UserModel, user_id)

    def get_user_by_username(self, username: str) -> UserModel | None:
        stmt = select(UserModel).where(UserModel.username == username)
        return self.db.execute(stmt).scalars().first()

    # 把用户的密码哈希换成新的并提交；提交失败先回滚再把异常往上抛
    def update_user_password(self, user: UserModel, new_hashed_password: str):
        user.password_hash = new_hashed_password
        try:
            self.db.commit()
        except Exception:
            self.db.rollback()
            raise
        self.db.refresh(user)