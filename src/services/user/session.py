'''
【Service 层 · 核心】登录会话的业务规则

作用
    决定"什么时候建会话、什么时候能刷新、什么时候作废"。
    所有判断都在这里；读写数据库交给 SessionRepository，生成 token 交给 jwt.py。

三个对外函数（其余带 _ 前缀的是内部辅助函数）
    start_session    登录成功后调用：建一行会话，签发 access + refresh
    refresh_session  POST /token/refresh：校验旧会话 → 作废 → 建新会话（refresh token 轮换）
    end_session      POST /token/logout：作废当前会话

调用链
    登录   routers/login.py → services/user/login.py → start_session
    刷新   routers/token.py → refresh_session → _get_valid_session → SessionRepository
    退出   routers/token.py → end_session     → _get_valid_session → SessionRepository

注意
    access token 不查会话表，所以退出后手里的 access token
    最多还能用 access_token_expire_minutes 分钟，之后就刷新不了了。
'''
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


# 会话无效（token 伪造 / 找不到 / 已作废 / 已过期）时抛出，router 层转成 401
class InvalidSessionError(Exception):
    pass


# 当前 UTC 时间
def _now() -> datetime:
    return datetime.now(timezone.utc)


# 计算 refresh token 的哈希，存库和比对都用它
# refresh token 本身是高熵随机串，用 sha256 即可，不需要 bcrypt 这种慢哈希
def _hash_token(token: str) -> str:
    return hashlib.sha256(token.encode()).hexdigest()


# SQLite 不保存时区，读出来是 naive datetime，统一按 UTC 处理
def _as_utc(dt: datetime) -> datetime:
    return dt if dt.tzinfo else dt.replace(tzinfo=timezone.utc)


# 建立新会话并签发一对 token
# 步骤：生成会话 id → 用它当 jti 签发 refresh token → 把 token 哈希存入会话表 → 再签发 access token
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


# 校验 refresh token，返回对应的有效会话（刷新和退出共用）
# 依次检查：签名/过期 → 会话存在且哈希一致 → 未作废 → 未过期；任一步失败抛出 InvalidSessionError
def _get_valid_session(refresh_token: str, repo: SessionRepository) -> SessionModel:
    # 1. token 本身是否合法（签名、exp、type）
    try:
        payload = decode_token(refresh_token, 'refresh')
    except jwt.InvalidTokenError as e:
        raise InvalidSessionError('Invalid refresh token') from e

    # 2. 用 jti 找会话，并确认就是当初签发的那个 token
    session = repo.get_by_id(payload['jti'])
    if session is None or not hmac.compare_digest(session.refresh_token_hash, _hash_token(refresh_token)):
        raise InvalidSessionError('Session not found')

    # 3. 是否已作废
    if session.revoked_at is not None:
        # 已作废的 refresh token 又被拿来用，说明 token 可能被盗，撤销该用户全部会话
        repo.revoke_all_by_user(session.user_id, _now())
        raise InvalidSessionError('Session revoked')

    # 4. 是否已过期（数据库层面的兜底）
    if _as_utc(session.expires_at) <= _now():
        raise InvalidSessionError('Session expired')

    return session


# 刷新：旧会话作废，换一个新会话和一对新 token（每个 refresh token 只能用一次）
def refresh_session(refresh_token: str, repo: SessionRepository) -> AuthTokens:
    session = _get_valid_session(refresh_token, repo)
    repo.revoke(session, _now())
    return start_session(session.user_id, repo)


# 退出：作废当前会话，此后这个 refresh token 无法再刷新
def end_session(refresh_token: str, repo: SessionRepository) -> None:
    session = _get_valid_session(refresh_token, repo)
    repo.revoke(session, _now())
