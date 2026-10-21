from pydantic import BaseModel

# 输入表单
'''
=======
一般用户
=======
'''
class LoginNormalUserRequest(BaseModel):
    username: str
    password: str
    email: str | None


class LoginNormalUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str

'''
=======
员工用户
=======
'''
class LoginStaffUserRequest(BaseModel):
    username: str
    password: str
    email: str | None

class LoginStaffUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str


'''
=======
管理员用户
=======
'''
class LoginAdminUserRequest(BaseModel):
    username: str
    password: str
    email: str | None


class LoginAdminUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str