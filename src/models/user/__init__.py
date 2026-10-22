# 导入所有表模型，让它们注册到 Base.metadata，启动建表时才能被创建
from .user import UserModel

__all__ = ["UserModel"]
