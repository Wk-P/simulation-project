'''
【Service 层 · 工具】JWT 的编码与解码

作用
    只管"把数据变成 token 字符串"和"把 token 字符串验证并还原成数据"。
    不碰数据库，不知道会话表的存在。

谁调用它
    services/user/session.py  签发 access / refresh token、验证 refresh token
    services/user/me.py       验证 access token

Token 结构: Header.Payload.Signature
Payload 字段
    sub  用户 id（JWT 规范要求为字符串）
    type 区分 access / refresh，防止拿 refresh token 当 access token 用
    iat  签发时间
    exp  过期时间
    jti  token 唯一 id；refresh token 的 jti 就是会话 id，用来查 sessions 表
'''
from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4

import jwt

from src.core.config import settings

TokenType = Literal['access', 'refresh']


# 通用签发：把 payload 用密钥签名成 token 字符串
# jti 不传时随机生成；签发 refresh token 时传入会话 id
def encode_token(user_id: int, token_type: TokenType, expires_at: datetime, jti: str | None = None) -> str:
    payload = {
        'sub': str(user_id),
        'type': token_type,
        'iat': datetime.now(timezone.utc),
        'exp': expires_at,
        'jti': jti or uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


# 签发 access token：有效期短（默认 15 分钟），不对应任何会话
def encode_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return encode_token(user_id, 'access', expires_at)


# 验证并解码：检查签名是否被篡改、是否过期、类型是否符合预期
# 任何一项不通过都抛出 jwt.InvalidTokenError，由调用方决定怎么处理
def decode_token(token: str, expected_type: TokenType) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={'require': ['sub', 'type', 'exp', 'jti']},
    )
    if payload['type'] != expected_type:
        raise jwt.InvalidTokenError(f'Expected {expected_type} token')
    return payload
