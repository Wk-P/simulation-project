'''
【Service 层】当前用户

作用
    token_authenticate  验证 access token，找出"这个请求是谁发的"
    user_get_me         把用户数据组装成 /me 的响应

调用链
    GET /me → routers/me.py
        → Depends(get_current_user)（routers/deps.py）→ token_authenticate → UserRepository
        → user_get_me

注意
    这里只验证 access token 的签名和过期时间，不查 sessions 表，所以速度快。
'''
import jwt

from .jwt import decode_token
from src.models.user.user import UserModel
from src.repositories.user.user import UserRepository
from src.schemas.user.me import GetMeResponse


# 未登录 / token 无效 / 用户不存在时抛出，router 层转成 401
class NotAuthenticatedError(Exception):
    pass


# 鉴权：解码 access token → 用 sub（用户 id）查出用户 → 确认用户仍然可用
def token_authenticate(token: str, repo: UserRepository) -> UserModel:
    try:
        payload = decode_token(token, 'access')
    except jwt.InvalidTokenError as e:
        raise NotAuthenticatedError('Invalid access token') from e

    user = repo.get_user_by_id(int(payload['sub']))
    if user is None or not user.active:
        raise NotAuthenticatedError('User not found or inactive')
    return user


# 把数据库里的用户转成响应格式（不返回 password_hash 等敏感字段）
def user_get_me(user: UserModel) -> GetMeResponse:
    return GetMeResponse(username=user.username, id=str(user.id), email=user.email)
