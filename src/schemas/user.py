from pydantic import BaseModel

# 输入表单
'''
=======
一般用户
=======
'''
class NormalUserRequest(BaseModel):
    username: str
    password: str
    email: str | None


class NormalUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str

'''
=======
员工用户
=======
'''
class StaffUserRequest(BaseModel):
    username: str
    password: str
    email: str | None

class StaffUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str


'''
=======
管理员用户
=======
'''
class AdminUserRequest(BaseModel):
    username: str
    password: str
    email: str | None


class AdminUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str
