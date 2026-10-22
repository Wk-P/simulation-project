'''
【Service 层】鉴权

作用
    authenticate_access_token  验证 access token，找出"这个请求是谁发的"

调用链
    任何需要登录的接口
        → Depends(get_current_user)（routers/deps.py）→ authenticate_access_token
            → verify_access_token（services/session/token.py）  验证签名和过期时间
            → UserRepository                                    按 sub 查出用户

注意
    这里只验证 access token 的签名和过期时间，不查 sessions 表，所以速度快。
'''
import jwt

from src.models.user.user import UserModel
from src.repositories.user.user import UserRepository
from src.services.session.token import verify_access_token


# 未登录 / token 无效 / 用户不存在时抛出，router 层转成 401
class NotAuthenticatedError(Exception):
    pass


# 收：access token 和 user_repo；做：验证 token → 用 sub（用户 id）查用户 → 确认用户可用；返回：用户
def authenticate_access_token(access_token: str, user_repo: UserRepository) -> UserModel:
    # 1. 验证 token
    try:
        payload = verify_access_token(access_token)
    except jwt.InvalidTokenError as e:
        raise NotAuthenticatedError('Invalid access token') from e

    # 2. 用 sub 查用户
    user_id = int(payload['sub'])
    user = user_repo.get_user_by_id(user_id)

    # 3. 用户不存在或已停用
    if user is None or not user.active:
        raise NotAuthenticatedError('User not found or inactive')

    return user
