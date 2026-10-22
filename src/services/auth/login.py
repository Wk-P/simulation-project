'''
【Service 层】登录

作用
    核对用户名和密码，通过后调用 start_session 建立会话、拿到 token。

调用链
    POST /login/user → routers/login.py → login_user
        → verify_user_credentials()  查用户 + 校验密码（UserRepository）
        → start_session()            建会话 + 签发 token（services/session/session.py）
'''
from src.services.user.password import verify_password
from src.services.session.session import start_session
from src.models.user.user import UserModel
from src.repositories.session.session import SessionRepository
from src.repositories.user.user import UserRepository
from src.schemas.auth.login import LoginUserResponse, LoginUserRequest


# 用户名或密码错误时抛出，router 层转成 401
class InvalidCredentialsError(Exception):
    pass


# 收：用户名、密码、user_repo；做：核对账号；返回：用户，用户不存在 / 已停用 / 密码错误都返回 None
def verify_user_credentials(username: str, password: str, user_repo: UserRepository) -> UserModel | None:
    user = user_repo.get_user_by_username(username)
    if not user or not user.active:
        return None
    if not verify_password(password, user.password_hash):
        return None
    return user


# 收：登录请求和两个 repo；做：核对账号 → 建会话 → 组装响应；返回：用户信息和 token
def login_user(request: LoginUserRequest, user_repo: UserRepository, session_repo: SessionRepository) -> LoginUserResponse:
    # 1. 核对用户名和密码
    user = verify_user_credentials(request.username, request.password, user_repo)
    if not user:
        raise InvalidCredentialsError("Invalid username or password")

    # 2. 建立会话并签发 token
    tokens = start_session(user.id, session_repo)

    # 3. 组装响应
    response = LoginUserResponse(
        username=user.username,
        user_id=str(user.id),
        email=user.email,
        message="Login successful",
        tokens=tokens,
    )
    return response
