import jwt

from .jwt import decode_token
from src.models.user.user import UserModel
from src.repositories.user.user import UserRepository
from src.schemas.user.me import GetMeResponse


class NotAuthenticatedError(Exception):
    pass


# 鉴权：验证 access token，返回当前用户（不查会话表）
def token_authenticate(token: str, repo: UserRepository) -> UserModel:
    try:
        payload = decode_token(token, 'access')
    except jwt.InvalidTokenError as e:
        raise NotAuthenticatedError('Invalid access token') from e

    user = repo.get_user_by_id(int(payload['sub']))
    if user is None or not user.active:
        raise NotAuthenticatedError('User not found or inactive')
    return user


# 组装当前用户信息
def user_get_me(user: UserModel) -> GetMeResponse:
    return GetMeResponse(username=user.username, id=str(user.id), email=user.email)
