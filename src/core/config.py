import os


# 全局配置，优先从环境变量读取
class Settings:
    def __init__(self):
        self.database_url: str = os.getenv('DATABASE_URL', 'sqlite:///./app.db')


settings = Settings()
