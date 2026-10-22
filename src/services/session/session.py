'''
【Service 层 · 核心】登录会话的业务规则

作用
    决定"什么时候建会话、什么时候能刷新、什么时候作废"。
    所有判断都在这里；读写数据库交给 SessionRepository，创建和验证 token 交给 token.py。

三个函数
    start_session    登录成功后调用：建一行会话，创建 access + refresh
    refresh_session  POST /token/refresh：验证旧会话 → 作废 → 建新会话（每个 refresh token 只能用一次）
    end_session      POST /token/logout：验证会话 → 作废

调用链
    登录   routers/login.py → services/auth/login.py → start_session
    刷新   routers/token.py → refresh_session → SessionRepository
    退出   routers/token.py → end_session     → SessionRepository

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
from src.models.session.session import SessionModel
from src.repositories.session.session import SessionRepository
from src.schemas.session.token import AuthTokens
from .token import create_access_token, create_refresh_token, verify_refresh_token


# 会话无效（token 伪造 / 找不到 / 已作废 / 已过期）时抛出，router 层转成 401
class InvalidSessionError(Exception):
    pass


# 收：用户 id 和 session_repo；做：建一行会话并创建一对 token；返回：access + refresh
def start_session(user_id: int, session_repo: SessionRepository) -> AuthTokens:
    # 1. 准备：当前时间、会话 id、refresh token 的过期时间
    now = datetime.now(timezone.utc)
    session_id = uuid4().hex
    expires_at = now + timedelta(days=settings.refresh_token_expire_days)

    # 2. 创建 refresh token（它的 jti 就是会话 id）
    refresh_token = create_refresh_token(user_id, expires_at, session_id)

    # 3. 数据库里只存 refresh token 的 sha256 哈希，不存原文
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()

    # 4. 存入 sessions 表
    session = SessionModel(
        id=session_id,
        user_id=user_id,
        refresh_token_hash=refresh_token_hash,
        expires_at=expires_at,
        created_at=now,
    )
    session_repo.create_session(session)

    # 5. 创建 access token（不入库）
    access_token = create_access_token(user_id)

    # 6. 组装并返回
    tokens = AuthTokens(access_token=access_token, refresh_token=refresh_token)
    return tokens


# 收：旧 refresh token 和 session_repo；做：验证旧会话 → 作废 → 开新会话；返回：一对新 token
def refresh_session(refresh_token: str, session_repo: SessionRepository) -> AuthTokens:
    # 1. token 本身是否合法（签名、exp、type）
    try:
        payload = verify_refresh_token(refresh_token)
    except jwt.InvalidTokenError as e:
        raise InvalidSessionError('Invalid refresh token') from e

    # 2. 用 jti 找会话，并确认就是当初签发的那个 token
    session = session_repo.get_session_by_id(payload['jti'])
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    if session is None or not hmac.compare_digest(session.refresh_token_hash, refresh_token_hash):
        raise InvalidSessionError('Session not found')

    # 3. 是否已作废：已作废的 refresh token 又被拿来用，说明可能被盗，撤销该用户全部会话
    now = datetime.now(timezone.utc)
    if session.revoked_at is not None:
        session_repo.revoke_sessions_by_user_id(session.user_id, now)
        raise InvalidSessionError('Session revoked')

    # 4. 是否已过期（SQLite 读出来没有时区，补上 UTC 再比较）
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise InvalidSessionError('Session expired')

    # 5. 作废旧会话
    session_repo.revoke_session(session, now)

    # 6. 开新会话
    tokens = start_session(session.user_id, session_repo)
    return tokens


# 收：refresh token 和 session_repo；做：验证会话 → 作废；返回：无（此后这个 refresh token 无法再刷新）
def end_session(refresh_token: str, session_repo: SessionRepository) -> None:
    # 1. token 本身是否合法（签名、exp、type）
    try:
        payload = verify_refresh_token(refresh_token)
    except jwt.InvalidTokenError as e:
        raise InvalidSessionError('Invalid refresh token') from e

    # 2. 用 jti 找会话，并确认就是当初签发的那个 token
    session = session_repo.get_session_by_id(payload['jti'])
    refresh_token_hash = hashlib.sha256(refresh_token.encode()).hexdigest()
    if session is None or not hmac.compare_digest(session.refresh_token_hash, refresh_token_hash):
        raise InvalidSessionError('Session not found')

    # 3. 是否已作废：同样视为被盗用，撤销该用户全部会话
    now = datetime.now(timezone.utc)
    if session.revoked_at is not None:
        session_repo.revoke_sessions_by_user_id(session.user_id, now)
        raise InvalidSessionError('Session revoked')

    # 4. 是否已过期
    expires_at = session.expires_at
    if expires_at.tzinfo is None:
        expires_at = expires_at.replace(tzinfo=timezone.utc)
    if expires_at <= now:
        raise InvalidSessionError('Session expired')

    # 5. 作废会话
    session_repo.revoke_session(session, now)
