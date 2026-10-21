from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from sqlalchemy.orm import Session

from src.db.session import get_db
from src.models.user.user import UserModel
from src.repositories.user.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.services.user.me import NotAuthenticatedError, token_authenticate

# 从请求头 Authorization: Bearer <token> 中取出 token
bearer_scheme = HTTPBearer(auto_error=False)


def get_user_repo(db: Session = Depends(get_db)) -> UserRepository:
    return UserRepository(db)


def get_session_repo(db: Session = Depends(get_db)) -> SessionRepository:
    return SessionRepository(db)


# 需要登录的接口依赖它，拿到的就是当前用户
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
