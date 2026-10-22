'''
【Schema 层】/me 相关的请求体和响应体

作用
    GetMeResponse          GET /me 的响应，不含 password_hash
    UpdatePasswordRequest  POST /me/password 的请求体

注意
    Field(min_length=8) 由 Pydantic 校验，不满足时 FastAPI 自动返回 422，不会进到 service；
    完整的密码格式规则在 services/user/password.py 里再检查一次。
'''
from pydantic import BaseModel, Field

# 当前用户由 access token 决定，不接收请求体
class GetMeResponse(BaseModel):
    username: str
    id: str
    email: str | None


# POST /me/password 的请求体：新密码至少 8 位
class UpdatePasswordRequest(BaseModel):
    old_password: str
    new_password: str = Field(min_length=8)
    