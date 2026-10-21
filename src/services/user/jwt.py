from datetime import datetime, timedelta, timezone
from typing import Literal
from uuid import uuid4

import jwt

from src.core.config import settings
from src.models.user import UserModel
from src.schemas.user.jwt import AuthTokens

TokenType = Literal['access', 'refresh']


'''
Token 结构: Header.Payload.Signature
Payload 字段
    sub  用户 id（JWT 规范要求为字符串）
    type 区分 access / refresh，防止拿 refresh token 当 access token 用
    iat  签发时间
    exp  过期时间
    jti  token 唯一 id，后续做注销 / 黑名单时使用
'''

def _encode_token(user: UserModel, token_type: TokenType, expires_delta: timedelta) -> str:
    now = datetime.now(timezone.utc)
    payload = {
        'sub': str(user.id),
        'type': token_type,
        'iat': now,
        'exp': now + expires_delta,
        'jti': uuid4().hex,
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def generate_token(user: UserModel) -> AuthTokens:
    return AuthTokens(
        access_token=_encode_token(user, 'access', timedelta(minutes=settings.access_token_expire_minutes)),
        refresh_token=_encode_token(user, 'refresh', timedelta(days=settings.refresh_token_expire_days)),
    )


# 校验签名、过期时间和 token 类型，失败抛出 jwt.InvalidTokenError
def decode_token(token: str, expected_type: TokenType) -> dict:
    payload = jwt.decode(
        token,
        settings.jwt_secret_key,
        algorithms=[settings.jwt_algorithm],
        options={'require': ['sub', 'type', 'exp']},
    )
    if payload['type'] != expected_type:
        raise jwt.InvalidTokenError(f'Expected {expected_type} token')
    return payload
