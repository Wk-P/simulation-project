from pydantic import BaseModel


# Token

class AuthTokens(BaseModel):
    access_token: str
    refresh_token: str


# 刷新 / 退出时客户端提交 refresh token
class RefreshTokenRequest(BaseModel):
    refresh_token: str
