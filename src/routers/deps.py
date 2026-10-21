'''
【Router 层 · 依赖】FastAPI 的 Depends 依赖集中放在这里

作用
    路由函数参数里写 Depends(xxx)，FastAPI 会在每次请求时自动调用 xxx，把结果传进来。
    这样路由函数不用自己创建数据库连接、repository，也不用自己解析请求头。

依赖链（箭头 = "需要先拿到"）
    get_user_repo     ← get_db                     （每个请求一个数据库连接）
    get_session_repo  ← get_db
    get_current_user  ← bearer_scheme + get_user_repo

用法
    任何需要登录的接口，参数里加 user: UserModel = Depends(get_current_user) 即可。
'''
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user.user import UserModel
from src.repositories.user.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.services.user.me import NotAuthenticatedError, token_authenticate

# 从请求头 Authorization: Bearer <token> 中取出 token
# auto_error=False：没带请求头时返回 None，由下面统一返回 401
bearer_scheme = HTTPBearer(auto_error=False)


# 提供用户表的 repository
def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


# 提供会话表的 repository
def get_session_repo(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


# 提供当前登录用户：取出 token → 交给 service 鉴权 → 失败转成 HTTP 401
def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(bearer_scheme),
    repo: UserRepository = Depends(get_user_repo),
) -> UserModel:
    if credentials is None:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, 'Not authenticated', headers={'WWW-Authenticate': 'Bearer'})
    try:
        return token_authenticate(credentials.credentials, repo)
    except NotAuthenticatedError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e), headers={'WWW-Authenticate': 'Bearer'}) from e
