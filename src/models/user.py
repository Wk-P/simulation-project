# import 

class UserModel:
    def __init__(self, username: str, password: str, email: str = None, admin: bool = False, staff: bool = False):
        self.username = username
        self.email = email
        self.password = password
        self.admin = admin
        self.staff = staff

        self.active = True



def create_user(username: str, password: str, email: str = None, admin: bool = False, staff: bool = False):
    return UserModel(username=username, password=password, email=email, admin=admin, staff=staff)


# 数据库操作
class UserDB:
    def __init__(self):
        pass
    def write_db(self, o: object):
        # 成功返回 True
        # 失败返回 False，附带原因
        pass
    def check_username_repeat(self, username: str) -> bool:
        # Implementation for checking username repetition
        # Check if username already exists
        pass
userDB = UserDB()