'''
【Service 层 · 工具】密码的哈希、校验和格式规则

作用
    hash_password          明文 → bcrypt 哈希（存进数据库的是它）
    verify_password        明文和哈希是否匹配（登录、改密码时校验旧密码）
    compare_password       新旧密码是否不同
    verify_password_style  密码格式是否合规（注册和改密码共用同一套规则）

谁调用它
    services/user/register.py、services/auth/、services/user/me.py
'''
from pwdlib import PasswordHash
from pwdlib.hashers.bcrypt import BcryptHasher
from string import ascii_letters, digits

# 全局共用的哈希器，只启用 bcrypt
password_hash = PasswordHash((BcryptHasher(),))

# 收：明文密码；做：bcrypt 加盐哈希；返回：哈希字符串
def hash_password(password: str) -> str:
    return password_hash.hash(password)

# 收：明文密码和数据库里的哈希；做：比对；返回：是否匹配
def verify_password(password: str, password_hash_value: str) -> bool:
    return password_hash.verify(password, password_hash_value)

# 收：旧密码和新密码；做：比较两者；返回：True 表示新旧不同（可以改）
def compare_password(old_password: str, new_password: str) -> bool:
    return not (old_password == new_password)


# 收：密码；做：检查长度 8-16、只含允许字符、字母数字特殊字符都有；返回：是否合规
def verify_password_style(password: str) -> bool:
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