from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4

import jwt

from src.core.config import settings

TokenType = Literal['access', 'refresh']


'''
Token 结构: Header.Payload.Signature
Payload 字段
    sub  用户 id（JWT 规范要求为字符串）
    type 区分 access / refresh，防止拿 refresh token 当 access token 用
    iat  签发时间
    exp  过期时间
    jti  token 唯一 id；refresh token 的 jti 就是会话 id，用来查 sessions 表
'''

def encode_token(user_id: int, token_type: TokenType, expires_at: datetime, jti: str | None = None) -> str:
    payload = {
        'sub': str(user_id),
        'type': token_type,
        'iat': datetime.now(timezone.utc),
        'exp': expires_at,
        'jti': jti or uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def encode_access_token(user_id: int) -> str:
    expires_at = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    return encode_token(user_id, 'access', expires_at)


# 校验签名、过期时间和 token 类型，失败抛出 jwt.InvalidTokenError
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
