'''
【Service 层 · 工具】JWT 的创建与验证

作用
    只管"把数据变成 token 字符串"和"把 token 字符串验证并还原成数据"。
    不碰数据库，不知道会话表的存在。

谁调用它
    services/session/session.py  签发 access / refresh token、验证 refresh token
    services/auth/authenticate.py  验证 access token

Token 结构: Header.Payload.Signature
Payload 字段
    sub  用户 id（JWT 规范要求为字符串）
    type 区分 access / refresh，防止拿 refresh token 当 access token 用
    iat  签发时间
    exp  过期时间
    jti  token 唯一 id；refresh token 的 jti 就是会话 id，用来查 sessions 表
'''
from datetime import datetime, timedelta, timezone
from uuid import uuid4

import jwt

from src.core.config import settings


# 签发 access token：有效期短（默认 15 分钟），不对应任何会话
def create_access_token(user_id: int) -> str:
    # 1. 算出过期时间：现在 + 15 分钟
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)

    # 2. 准备要写进 token 的内容
    payload = {
        'sub': str(user_id),            # 属于谁
        'type': 'access',               # 是哪种 token
        'iat': datetime.now(timezone.utc),  # 什么时候签发的
        'exp': expires_at,              # 什么时候过期
        'jti': uuid4().hex,             # 这张 token 的编号，随机生成
    }

    # 3. 用密钥盖章，变成一长串字符
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# 签发 refresh token：有效期长，jti 必须是会话 id，之后靠它去 sessions 表查这一行
def create_refresh_token(user_id: int, expires_at: datetime, session_id: str) -> str:
    # 1. 准备要写进 token 的内容（过期时间由调用方算好传进来）
    payload = {
        'sub': str(user_id),
        'type': 'refresh',
        'iat': datetime.now(timezone.utc),
        'exp': expires_at,
        'jti': session_id,              # 编号 = 会话 id
    }

    # 2. 用密钥盖章
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# 验证 access token，返回里面的内容；签名被改、过期、不是 access 类型都会抛出 jwt.InvalidTokenError
def verify_access_token(token: str) -> dict:
    # 1. 验章并读出内容（jwt.decode 会自动检查签名和过期时间）
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={'require': ['sub', 'type', 'exp', 'jti']},  # 这四项缺一不可
    )

    # 2. 检查类型：拿 refresh token 来冒充 access token 要被拒绝
    if payload['type'] != 'access':
        raise jwt.InvalidTokenError('Expected access token')

    return payload


# 验证 refresh token，返回里面的内容；签名被改、过期、不是 refresh 类型都会抛出 jwt.InvalidTokenError
def verify_refresh_token(token: str) -> dict:
    # 1. 验章并读出内容
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={'require': ['sub', 'type', 'exp', 'jti']},
    )

    # 2. 检查类型：拿 access token 来冒充 refresh token 要被拒绝
    if payload['type'] != 'refresh':
        raise jwt.InvalidTokenError('Expected refresh token')

    return payload
