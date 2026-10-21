from pydantic import BaseModel

# 输入表单
'''
=======
一般用户
=======
'''
class RegisterNormalUserRequest(BaseModel):
    username: str
    password: str
    email: str | None


class RegisterNormalUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str

'''
=======
员工用户
=======
'''
class RegisterStaffUserRequest(BaseModel):
    username: str
    password: str
    email: str | None

class RegisterStaffUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str


'''
=======
管理员用户
=======
'''
class RegisterAdminUserRequest(BaseModel):
    username: str
    password: str
    email: str | None


class RegisterAdminUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str