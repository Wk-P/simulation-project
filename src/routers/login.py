'''
【Router 层】登录接口

    POST /login/user   用户名 + 密码 → 用户信息 + access token + refresh token

职责
    只处理 HTTP：接收请求体、注入 repository、调用 service、把业务异常转成 HTTP 状态码。
    登录逻辑在 services/auth/login.py。
'''
from fastapi import APIRouter, Depends, HTTPException, status

from src.repositories.session.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.routers.deps import get_session_repo, get_user_repo
from src.schemas.auth.login import LoginUserRequest, LoginUserResponse
from src.services.auth.login import InvalidCredentialsError, login_user

router = APIRouter(prefix="/login")


# 登录：需要两个 repository —— 查用户（UserRepository）、建会话（SessionRepository）
@router.post('/user')
def post_login_user(
    request: LoginUserRequest,
    user_repo: UserRepository = Depends(get_user_repo),
    session_repo: SessionRepository = Depends(get_session_repo),
) -> LoginUserResponse:
    try:
        response = login_user(request, user_repo, session_repo)
    except InvalidCredentialsError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e
    return response
