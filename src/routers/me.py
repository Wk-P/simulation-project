'''
【Router 层】当前用户

    GET  /me            请求头 Authorization: Bearer <access_token> → 当前用户信息
    POST /me/password   请求体 {old_password, new_password} → 204，成功后该用户所有会话作废

职责
    鉴权交给 Depends(get_current_user)（routers/deps.py）：
    执行到函数体时，user 一定是已登录的有效用户；token 无效会在进入函数前就返回 401。
    业务判断交给 services/user/me.py；这里只把 service 抛出的异常翻译成 HTTP 400 和提示语。
'''
from fastapi import APIRouter, Depends
from fastapi import HTTPException
from src.models.user.user import UserModel
from src.routers.deps import get_current_user, get_user_repo, get_session_repo
from src.schemas.user.me import GetMeResponse, UpdatePasswordRequest
from src.services.user.me import get_me_response, update_me_password, SamePasswordError, WeakPasswordError, WrongOldPasswordError
from src.repositories.user.user import UserRepository
from src.repositories.session.session import SessionRepository

router = APIRouter(prefix="/me")


# 返回当前登录用户的信息
@router.get('')
def get_me(user: UserModel = Depends(get_current_user)) -> GetMeResponse:
    response = get_me_response(user)
    return response


# 修改当前用户的密码：三种业务错误分别转成带不同提示的 400，新密码太短由 schema 返回 422
@router.post('/password', status_code=204)
def update_password(request: UpdatePasswordRequest, user: UserModel = Depends(get_current_user), user_repo: UserRepository = Depends(get_user_repo), session_repo: SessionRepository = Depends(get_session_repo)):
    try:
        update_me_password(request.old_password, request.new_password, user, user_repo, session_repo)
    except WrongOldPasswordError:
        raise HTTPException(400, "旧密码不正确")
    except SamePasswordError:
        raise HTTPException(400, "新密码不能与旧密码相同")
    except WeakPasswordError:
        raise HTTPException(400, "新密码需 8-16 位，包含字母、数字和特殊字符")
