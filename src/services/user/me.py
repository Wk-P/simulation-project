'''
【Service 层】当前用户

作用
    get_me_response  把用户数据组装成 /me 的响应

调用链
    GET /me → routers/me.py
        → Depends(get_current_user)（routers/deps.py）→ services/auth/authenticate.py
        → get_me_response
'''
from src.models.user.user import UserModel
from src.schemas.user.me import GetMeResponse


# 收：数据库里的用户；做：去掉 password_hash 等敏感字段；返回：/me 的响应
def get_me_response(user: UserModel) -> GetMeResponse:
    response = GetMeResponse(username=user.username, id=str(user.id), email=user.email)
    return response
