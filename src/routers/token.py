'''
【Router 层】token 刷新与退出

    POST /token/refresh   body: {refresh_token} → 一对新 token（旧 refresh token 作废）
    POST /token/logout    body: {refresh_token} → 204，会话作废

使用时机（客户端视角）
    访问接口返回 401 → 说明 access token 过期 → 调 /token/refresh 换新的 → 重试原请求
    /token/refresh 也返回 401 → 说明会话已失效 → 让用户重新登录

职责
    只处理 HTTP，规则在 services/user/session.py。
'''
from fastapi import APIRouter, Depends, HTTPException, status

from src.repositories.user.session import SessionRepository
from src.routers.deps import get_session_repo
from src.schemas.user.jwt import AuthTokens, RefreshTokenRequest
from src.services.user.session import InvalidSessionError, end_session, refresh_session

router = APIRouter(prefix="/token")


# 刷新：用 refresh token 换一对新 token，旧 refresh token 同时作废
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
