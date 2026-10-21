from string import ascii_letters, digits

from src.models.user import UserModel
from src.repositories.user import UserRepository, UsernameAlreadyExistsError
from src.schemas.user.register import RegisterNormalUserRequest, RegisterNormalUserResponse, RegisterStaffUserRequest, RegisterStaffUserResponse, RegisterAdminUserRequest, RegisterAdminUserResponse
from .password import password_hasher

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

def validation(user: RegisterNormalUserRequest | RegisterStaffUserRequest | RegisterAdminUserRequest) -> bool:
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





# 三种用户共用的注册流程，成功返回新用户，用户名重复返回 None
def _create_user(repo: UserRepository, user: RegisterNormalUserRequest | RegisterStaffUserRequest | RegisterAdminUserRequest, admin: bool = False, staff: bool = False) -> UserModel | None:
    if repo.exists_by_username(user.username):
        return None
    new_user = UserModel(
        username=user.username,
        password_hash=password_hasher(user.password),
        email=user.email,
        admin=admin,
        staff=staff,
    )
    try:
        return repo.create(new_user)
    except UsernameAlreadyExistsError:
        return None

# 普通用户
def user_register_svc(user: RegisterNormalUserRequest, repo: UserRepository) -> RegisterNormalUserResponse:
    if not validation(user):
        return RegisterNormalUserResponse(username=user.username, user_id=None, email=None, message="Invalid user input")

    created = _create_user(repo, user)
    if created is None:
        return RegisterNormalUserResponse(username=user.username, user_id=None, email=None, message="Username already exists")

    return RegisterNormalUserResponse(username=created.username, user_id=str(created.id), email=created.email, message="User registered successfully")

# 员工用户
def staff_register_svc(staff: RegisterStaffUserRequest, repo: UserRepository) -> RegisterStaffUserResponse:
    if not validation(staff):
        return RegisterStaffUserResponse(username=staff.username, user_id=None, email=None, message="Invalid staff input")

    created = _create_user(repo, staff, staff=True)
    if created is None:
        return RegisterStaffUserResponse(username=staff.username, user_id=None, email=None, message="Username already exists")

    return RegisterStaffUserResponse(username=created.username, user_id=str(created.id), email=created.email, message="Staff registered successfully")


# 管理员用户
def admin_register_svc(admin: RegisterAdminUserRequest, repo: UserRepository) -> RegisterAdminUserResponse:
    if not validation(admin):
        return RegisterAdminUserResponse(username=admin.username, user_id=None, email=None, message="Invalid admin input")

    created = _create_user(repo, admin, admin=True)
    if created is None:
        return RegisterAdminUserResponse(username=admin.username, user_id=None, email=None, message="Username already exists")

    return RegisterAdminUserResponse(username=created.username, user_id=str(created.id), email=created.email, message="Admin registered successfully")
