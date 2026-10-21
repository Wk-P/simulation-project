'''
【Router 层】当前用户

    GET /me   请求头 Authorization: Bearer <access_token> → 当前用户信息

职责
    鉴权交给 Depends(get_current_user)（routers/deps.py）：
    执行到函数体时，user 一定是已登录的有效用户；token 无效会在进入函数前就返回 401。
'''
from fastapi import APIRouter, Depends

from src.models.user.user import UserModel
from src.routers.deps import get_current_user
from src.schemas.user.me import GetMeResponse
from src.services.user.me import user_get_me

router = APIRouter(prefix="/me")


# 返回当前登录用户的信息
@router.get('')
def user_me(user: UserModel = Depends(get_current_user)) -> GetMeResponse:
    return user_get_me(user)
