from .password import password_verify
from src.models.user import UserModel
from src.repositories.user import UserRepository
from src.schemas.user.login import LoginUserResponse, LoginUserRequest
from .jwt import generate_token

# 验证账户密码
def login(username: str, password: str, repo: UserRepository) -> UserModel | None:
    user = repo.get_user_by_username(username)
    if not user:
        return None
    if not password_verify(password, user.password_hash):
        return None
    return user

# 用户登录服务
def user_login_svc(user: LoginUserRequest, repo: UserRepository) -> LoginUserResponse:
    logged_in_user = login(user.username, user.password, repo)
    if not logged_in_user:
        raise ValueError("Invalid username or password")

    # 下发token
    tokens = generate_token(logged_in_user)

    return LoginUserResponse(
        username=logged_in_user.username,
        user_id=str(logged_in_user.id),
        email=logged_in_user.email,
        message="Login successful",
        tokens=tokens,
    )