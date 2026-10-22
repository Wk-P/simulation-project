from string import ascii_letters, digits

from src.models.user.user import UserModel
from src.repositories.user.user import UserRepository, UsernameAlreadyExistsError
from src.schemas.user.register import RegisterNormalUserRequest, RegisterNormalUserResponse, RegisterStaffUserRequest, RegisterStaffUserResponse, RegisterAdminUserRequest, RegisterAdminUserResponse
from .password import hash_password

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

def validate_register_request(request: RegisterNormalUserRequest | RegisterStaffUserRequest | RegisterAdminUserRequest) -> bool:
    username = request.username
    password = request.password

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


# 三种用户共用的注册流程（用了三次，所以抽出来）：成功返回新用户，用户名重复返回 None
def create_user_account(user_repo: UserRepository, request: RegisterNormalUserRequest | RegisterStaffUserRequest | RegisterAdminUserRequest, admin: bool = False, staff: bool = False) -> UserModel | None:
    if user_repo.exists_by_username(request.username):
        return None
    new_user = UserModel(
        username=request.username,
        password_hash=hash_password(request.password),
        email=request.email,
        admin=admin,
        staff=staff,
    )
    try:
        created_user = user_repo.create_user(new_user)
    except UsernameAlreadyExistsError:
        return None
    return created_user


# 普通用户
def register_user(request: RegisterNormalUserRequest, user_repo: UserRepository) -> RegisterNormalUserResponse:
    if not validate_register_request(request):
        response = RegisterNormalUserResponse(username=request.username, user_id=None, email=None, message="Invalid user input")
        return response

    created_user = create_user_account(user_repo, request)
    if created_user is None:
        response = RegisterNormalUserResponse(username=request.username, user_id=None, email=None, message="Username already exists")
        return response

    response = RegisterNormalUserResponse(username=created_user.username, user_id=str(created_user.id), email=created_user.email, message="User registered successfully")
    return response


# 员工用户
def register_staff(request: RegisterStaffUserRequest, user_repo: UserRepository) -> RegisterStaffUserResponse:
    if not validate_register_request(request):
        response = RegisterStaffUserResponse(username=request.username, user_id=None, email=None, message="Invalid staff input")
        return response

    created_user = create_user_account(user_repo, request, staff=True)
    if created_user is None:
        response = RegisterStaffUserResponse(username=request.username, user_id=None, email=None, message="Username already exists")
        return response

    response = RegisterStaffUserResponse(username=created_user.username, user_id=str(created_user.id), email=created_user.email, message="Staff registered successfully")
    return response


# 管理员用户
def register_admin(request: RegisterAdminUserRequest, user_repo: UserRepository) -> RegisterAdminUserResponse:
    if not validate_register_request(request):
        response = RegisterAdminUserResponse(username=request.username, user_id=None, email=None, message="Invalid admin input")
        return response

    created_user = create_user_account(user_repo, request, admin=True)
    if created_user is None:
        response = RegisterAdminUserResponse(username=request.username, user_id=None, email=None, message="Username already exists")
        return response

    response = RegisterAdminUserResponse(username=created_user.username, user_id=str(created_user.id), email=created_user.email, message="Admin registered successfully")
    return response
