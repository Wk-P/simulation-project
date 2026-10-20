from fastapi import FastAPI

app = FastAPI()
# 数据库操作
class DB:
    def __init__(self):
        pass
    def write_db(self, o: object):
        # 成功返回 True
        # 失败返回 False，附带原因
        pass
    def check_username(self, username):
        pass
db = DB()

def validation():
    # 用户名输入是否合法
    # 密码输入是否合法


    # 校验完全通过没问题
    pass

# 数据类型
class User:
    def __init__(self, username, password):
        username = username
        hashed_password = self.hash_password(password)

    def hash_password(self, password):
        pass



@app.post('/register')
def user_register():
    # 解析http和数据，调用业务逻辑
    username = None
    password = None

    # call validation function
    validationResult = validation()

    # ========
    # 用户名是否重复校验
    checkResult = db.check_username(None)
    if checkResult == True:     # 用户名重复
        # 返回状态码，
        pass



    # =========
    # 校验结束
    if validationResult == True: # username 和 password 通过校验
        # 1. 加密密码，并且生成数据对象
        user = User(username, password)

        # 2. 写入数据库
        dbResult = db.write_db(user)
        if dbResult == True: # 成功写入
            # 状态码 201 返回前端正确内容
            pass
        else:
            # 写入失败，服务器错误5xx，记录并返回状态码和前端信息
            pass
    else:   # 没通过校验
        # 拿到状态码，返回给前端信息
        pass