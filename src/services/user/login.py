from string import ascii_letters, digits

from pwdlib import PasswordHash
from src.models.user import UserModel
from src.repositories.user import UserRepository, UsernameAlreadyExistsError
from src.schemas.user.register import RegisterNormalUserRequest, RegisterNormalUserResponse, RegisterStaffUserRequest, RegisterStaffUserResponse, RegisterAdminUserRequest, RegisterAdminUserResponse


# 验证账户密码
def login(username: str, password: str, repo: UserRepository) -> UserModel | None:
    user = repo.get_user_by_username(username)
    if not user:
        return None
    if not PasswordHash.verify(password, user.password_hash):
        return None
    return user

# 普通用户
def user_login_svc(user: RegisterNormalUserRequest, repo: UserRepository) -> RegisterNormalUserResponse:
    logged_in_user = login(user.username, user.password, repo)
    if not logged_in_user:
        raise ValueError("Invalid username or password")
    return RegisterNormalUserResponse(
        username=logged_in_user.username,
        user_id=logged_in_user.id,
        email=logged_in_user.email,
        message="Login successful"
    )

# 员工用户
def staff_login_svc(user: RegisterStaffUserRequest, repo: UserRepository) -> RegisterStaffUserResponse:
    logged_in_user = login(user.username, user.password, repo)
    if not logged_in_user:
        raise ValueError("Invalid username or password")
    return RegisterStaffUserResponse(
        username=logged_in_user.username,
        user_id=logged_in_user.id,
        email=logged_in_user.email,
        message="Login successful"
    )

# 管理员用户
def admin_login_svc(user: RegisterAdminUserRequest, repo: UserRepository) -> RegisterAdminUserResponse:
    logged_in_user = login(user.username, user.password, repo)
    if not logged_in_user:
        raise ValueError("Invalid username or password")
    return RegisterAdminUserResponse(
        username=logged_in_user.username,
        user_id=logged_in_user.id,
        email=logged_in_user.email,
        message="Login successful"
    )