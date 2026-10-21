from pydantic import BaseModel
from .jwt import AuthTokens
# 输入表单
'''
=======
所有用户
=======
'''
class LoginUserRequest(BaseModel):
    username: str
    password: str


class LoginUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str
    tokens: AuthTokens


