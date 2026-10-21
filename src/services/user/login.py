'''
【Service 层】登录

作用
    核对用户名和密码，通过后调用 start_session 建立会话、拿到 token。

调用链
    POST /login/user → routers/login.py → user_login_svc
        → login()          查用户 + 校验密码（UserRepository）
        → start_session()  建会话 + 签发 token（services/user/session.py）
'''
from .password import password_verify
from .session import start_session
from src.models.user.user import UserModel
from src.repositories.user.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.schemas.user.login import LoginUserResponse, LoginUserRequest


# 用户名或密码错误时抛出，router 层转成 401
class InvalidCredentialsError(Exception):
    pass


# 验证账户密码：用户不存在 / 已停用 / 密码错误都返回 None
def login(username: str, password: str, repo: UserRepository) -> UserModel | None:
    user = repo.get_user_by_username(username)
    if not user or not user.active:
        return None
    if not password_verify(password, user.password_hash):
        return None
    return user

# 用户登录服务：验证通过 → 建立会话 → 返回用户信息和 token
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
