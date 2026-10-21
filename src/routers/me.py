from fastapi import APIRouter, Depends

from src.models.user.user import UserModel
from src.routers.deps import get_current_user
from src.schemas.user.me import GetMeResponse
from src.services.user.me import user_get_me

router = APIRouter(prefix="/me")


# get_current_user 负责从 Authorization 头取出 access token 并鉴权
@router.get('')
def user_me(user: UserModel = Depends(get_current_user)) -> GetMeResponse:
    return user_get_me(user)
