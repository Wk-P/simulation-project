from .password import password_verify
from .session import start_session
from src.models.user.user import UserModel
from src.repositories.user.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.schemas.user.login import LoginUserResponse, LoginUserRequest


class InvalidCredentialsError(Exception):
    pass


# 验证账户密码
def login(username: str, password: str, repo: UserRepository) -> UserModel | None:
    user = repo.get_user_by_username(username)
    if not user or not user.active:
        return None
    if not password_verify(password, user.password_hash):
        return None
    return user

# 用户登录服务
def user_login_svc(user: LoginUserRequest, user_repo: UserRepository, session_repo: SessionRepository) -> LoginUserResponse:
    logged_in_user = login(user.username, user.password, user_repo)
    if not logged_in_user:
        raise InvalidCredentialsError("Invalid username or password")

    # 建立会话并签发 token
    tokens = start_session(logged_in_user.id, session_repo)

    return LoginUserResponse(
        username=logged_in_user.username,
        user_id=str(logged_in_user.id),
        email=logged_in_user.email,
        message="Login successful",
        tokens=tokens,
    )
