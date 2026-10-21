from src.models.user import UserModel
from pydantic import BaseModel
from src.models.user import userDB
from string import ascii_letters, digits

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
    admin: bool = False
    staff: bool = False
    active: bool = True


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
    admin: bool = False
    staff: bool = True
    active: bool = True

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
    admin: bool = True
    staff: bool = False
    active: bool = True


class AdminUserResponse(BaseModel):
    username: str
    user_id: str | None
    email: str | None
    message: str


'''
后端再次验证输入
1. 用户名是否为空
2. 密码是否为空
3. 用户名要求
    禁止使用纯数字
    特殊字符只允许'_'
    禁止'_'开头
    长度不超过20个字符
    只允许英文字符
4. 密码要求
    字符组合
    【数字】【英文字符】【英文特殊字符'*''-''+''!''@''~''.''?'】
    三个必须都包含
    长度不超过16个字符
    长度最少8个字符
    只允许英文字符
'''

def validation(user: NormalUserRequest | StaffUserRequest | AdminUserRequest) -> bool:
    username = user.username
    password = user.password

    # 用户名仅允许英文字母、数字和下划线。
    if not 1 <= len(username) <= 20:
        return False
    if username.startswith('_') or username.isdecimal():
        return False
    if any(char not in ascii_letters + digits + '_' for char in username):
        return False

    # 密码必须同时包含英文字母、数字和指定特殊字符。
    special_chars = '*-+!@~.?'
    if not 8 <= len(password) <= 16:
        return False
    if any(char not in ascii_letters + digits + special_chars for char in password):
        return False
    if not any(char in ascii_letters for char in password):
        return False
    if not any(char in digits for char in password):
        return False
    if not any(char in special_chars for char in password):
        return False

    return True


"""
普通用户
"""
def user_register_svc(user: NormalUserRequest) -> NormalUserResponse:
    if not validation(user):
        return NormalUserResponse(username=user.username, user_id=None, email=None, message="Invalid user input")
    # 继续注册逻辑
    if userDB.check_username(user.username):
        return NormalUserResponse(username=user.username, user_id=None, email=None, message="Username already exists")

    # 生成返回数据
    responseUserInfo = NormalUserResponse(
        username=user.username,
        user_id="some_generated_id",  # Replace with actual ID generation logic
        email=user.email,
        message="User registered successfully"
    )

    return NormalUserResponse(username=user.username, user_id=responseUserInfo.user_id, email=user.email, message=responseUserInfo.message)



def staff_register_svc(staff: StaffUserRequest) -> StaffUserResponse:
    if not validation(staff):
        return StaffUserResponse(username=staff.username, user_id=None, email=None, message="Invalid staff input")
    # 继续注册逻辑
    if userDB.check_username(staff.username):
        return StaffUserResponse(username=staff.username, user_id=None, email=None, message="Username already exists")

    # 生成返回数据
    responseUserInfo = StaffUserResponse(
        username=staff.username,
        user_id="some_generated_id",  # Replace with actual ID generation logic
        email=staff.email,
        message="Staff registered successfully"
    )

    return StaffUserResponse(username=staff.username, user_id=responseUserInfo.user_id, email=staff.email, message=responseUserInfo.message)



def admin_register_svc(admin: AdminUserRequest) -> AdminUserResponse:
    if not validation(admin):
        return AdminUserResponse(username=admin.username, user_id=None, email=None, message="Invalid admin input")
    # 继续注册逻辑
    if userDB.check_username(admin.username):
        return AdminUserResponse(username=admin.username, user_id=None, email=None, message="Username already exists")

    # 生成返回数据
    responseUserInfo = AdminUserResponse(
        username=admin.username,
        user_id="some_generated_id",  # Replace with actual ID generation logic
        email=admin.email,
        message="Admin registered successfully"
    )

    return AdminUserResponse(username=admin.username, user_id=responseUserInfo.user_id, email=admin.email, message=responseUserInfo.message)
