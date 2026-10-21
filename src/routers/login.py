from fastapi import APIRouter, Depends, HTTPException, status

from src.repositories.user.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.routers.deps import get_session_repo, get_user_repo
from src.schemas.user.login import LoginUserRequest, LoginUserResponse
from src.services.user.login import InvalidCredentialsError, user_login_svc

router = APIRouter(prefix="/login")


@router.post('/user')
def user_login(
    user: LoginUserRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
) -> LoginUserResponse:
    try:
        return user_login_svc(user, user_repo, session_repo)
    except InvalidCredentialsError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e
