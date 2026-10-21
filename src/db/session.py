from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from src.core.config import settings

# SQLite 默认禁止跨线程使用连接，FastAPI 同步路由运行在线程池中，需要关闭该检查
connect_args = {'check_same_thread': False} if settings.database_url.startswith('sqlite') else {}

engine = create_engine(settings.database_url, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


# 每个请求一个 session，请求结束后关闭
def get_db() -> Iterator[Session]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
