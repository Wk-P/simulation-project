'''
【Service 层】当前用户

作用
    get_me_response     把用户数据组装成 /me 的响应
    update_me_password  校验旧密码和新密码 → 更新密码哈希 → 作废该用户所有会话

调用链
    GET /me → routers/me.py
        → Depends(get_current_user)（routers/deps.py）→ services/auth/authenticate.py
        → get_me_response

    POST /me/password → routers/me.py
        → update_me_password → UserRepository.update_user_password
                             → SessionRepository.revoke_sessions_by_user_id

注意
    当前设备的会话也会被作废（access token 里没有会话 id，分不出哪个是当前设备），
    前端改完密码后应让用户重新登录。
'''
from src.models.user.user import UserModel
from src.schemas.user.me import GetMeResponse
from src.services.user.password import compare_password, verify_password_style, hash_password, verify_password
from src.repositories.user.user import UserRepository
from src.repositories.session.session import SessionRepository
from datetime import datetime, timezone

# 改密码失败的三种原因，router 层分别转成带不同提示的 400
class WrongOldPasswordError(Exception): pass  # 旧密码与数据库里的哈希不匹配
class SamePasswordError(Exception): pass      # 新密码和旧密码一样
class WeakPasswordError(Exception): pass      # 新密码不符合格式要求



# 收：数据库里的用户；做：去掉 password_hash 等敏感字段；返回：/me 的响应
def get_me_response(user: UserModel) -> GetMeResponse:
    response = GetMeResponse(username=user.username, id=str(user.id), email=user.email)
    return response


# 收：新旧密码、当前用户和两个 repo；做：校验 → 存新哈希 → 作废所有会话；返回：无（失败时抛上面三种异常）
def update_me_password(old_password: str, new_password: str, user: UserModel, user_repo: UserRepository, session_repo: SessionRepository):
    # 1. 旧密码是否正确（和数据库里的哈希比对）
    if not verify_password(old_password, user.password_hash):
        raise WrongOldPasswordError()

    # 2. 新旧密码不能相同
    if not compare_password(old_password, new_password):
        raise SamePasswordError()

    # 3. 新密码是否符合格式（和注册时同一套规则）
    if not verify_password_style(new_password):
        raise WeakPasswordError()

    # 4. 只存哈希，不存明文
    user_repo.update_user_password(user, hash_password(new_password))

    # 5. 作废该用户所有仍有效的会话，其他设备的 refresh token 从此无法刷新
    now = datetime.now(timezone.utc)
    session_repo.revoke_sessions_by_user_id(user.id, now)
