import hashlib
import hmac
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from src.core.config import settings
from src.models.user.session import SessionModel
from src.repositories.user.session import SessionRepository
from src.schemas.user.jwt import AuthTokens
from .jwt import decode_token, encode_access_token, encode_token


class InvalidSessionError(Exception):
    pass


'''
会话流程
1. 登录   start_session    建一行会话，签发 access + refresh
2. 刷新   refresh_session  校验会话 → 作废旧会话 → 建新会话（refresh token 轮换）
3. 退出   end_session      作废会话
access token 不查会话表，最多在退出后继续存活 access_token_expire_minutes 分钟
'''

def _now() -> datetime:
    return datetime.now(timezone.utc)


# refresh token 本身是高熵随机串，用 sha256 即可，不需要 bcrypt 这种慢哈希
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# SQLite 不保存时区，读出来是 naive datetime，统一按 UTC 处理
def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


def start_session(user_id: int, repo: SessionRepository) -> AuthTokens:
    now = _now()
    session_id = uuid4().hex
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)
    refresh_token = encode_token(user_id, 'refresh', expires_at, jti=session_id)

    repo.create(SessionModel(
        id=session_id,
        user_id=user_id,
        refresh_token_hash=_hash_token(refresh_token),
        expires_at=expires_at,
        created_at=now,
    ))
    return AuthTokens(access_token=encode_access_token(user_id), refresh_token=refresh_token)


# 校验 refresh token 并返回对应的有效会话，任何一步不通过都抛出 InvalidSessionError
def _get_valid_session(refresh_token: str, repo: SessionRepository) -> SessionModel:
    try:
        payload = decode_token(refresh_token, 'refresh')
    except jwt.InvalidTokenError as e:
        raise InvalidSessionError('Invalid refresh token') from e

    session = repo.get_by_id(payload['jti'])
    if session is None or not hmac.compare_digest(session.refresh_token_hash, _hash_token(refresh_token)):
        raise InvalidSessionError('Session not found')

    if session.revoked_at is not None:
        # 已作废的 refresh token 又被拿来用，说明 token 可能被盗，撤销该用户全部会话
        repo.revoke_all_by_user(session.user_id, _now())
        raise InvalidSessionError('Session revoked')

    if _as_utc(session.expires_at) <= _now():
        raise InvalidSessionError('Session expired')

    return session


def refresh_session(refresh_token: str, repo: SessionRepository) -> AuthTokens:
    session = _get_valid_session(refresh_token, repo)
    repo.revoke(session, _now())
    return start_session(session.user_id, repo)


def end_session(refresh_token: str, repo: SessionRepository) -> None:
    session = _get_valid_session(refresh_token, repo)
    repo.revoke(session, _now())
