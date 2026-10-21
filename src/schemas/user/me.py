from pydantic import BaseModel

# 当前用户由 access token 决定，不接收请求体
class GetMeResponse(BaseModel):
    username: str
    id: str
    email: str | None
