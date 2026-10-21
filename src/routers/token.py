from fastapi import APIRouter, Depends, HTTPException, status

from src.repositories.user.session import SessionRepository
from src.routers.deps import get_session_repo
from src.schemas.user.jwt import AuthTokens, RefreshTokenRequest
from src.services.user.session import InvalidSessionError, end_session, refresh_session

router = APIRouter(prefix="/token")


# 用 refresh token 换一对新 token，旧 refresh token 同时作废
@router.post('/refresh')
def token_refresh(body: RefreshTokenRequest, repo: SessionRepository = Depends(get_session_repo)) -> AuthTokens:
    try:
        return refresh_session(body.refresh_token, repo)
    except InvalidSessionError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e


# 退出登录：作废当前会话
@router.post('/logout', status_code=status.HTTP_204_NO_CONTENT)
def token_logout(body: RefreshTokenRequest, repo: SessionRepository = Depends(get_session_repo)) -> None:
    try:
        end_session(body.refresh_token, repo)
    except InvalidSessionError as e:
        raise HTTPException(status.HTTP_401_UNAUTHORIZED, str(e)) from e
