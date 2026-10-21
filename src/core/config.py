import os


# 全局配置，优先从环境变量读取
class Settings:
    def __init__(self):
        self.database_url: str = os.getenv('DATABASE_URL', 'sqlite:///./app.db')

        # JWT 签名密钥，生产环境必须通过环境变量设置为足够长的随机串
        self.jwt_secret_key: str = os.getenv('JWT_SECRET_KEY', 'dev-only-insecure-secret-change-me-32b')
        self.jwt_algorithm: str = os.getenv('JWT_ALGORITHM', 'HS256')
        self.access_token_expire_minutes: int = int(os.getenv('ACCESS_TOKEN_EXPIRE_MINUTES', '15'))
        self.refresh_token_expire_days: int = int(os.getenv('REFRESH_TOKEN_EXPIRE_DAYS', '7'))


settings = Settings()
