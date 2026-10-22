from contextlib import asynccontextmanager

from fastapi import FastAPI

from src.db.base import Base
from src.db.session import engine
from src.models.user import user  # noqa: F401  注册表模型到 Base.metadata
from src.models.session import session  # noqa: F401
from src.routers.register import router as register_router
from src.routers.login import router as login_router
from src.routers.me import router as me_router
from src.routers.token import router as token_router

# 启动时建表（后续引入 Alembic 迁移后应移除）
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(lifespan=lifespan)
app.include_router(register_router)
app.include_router(login_router)
app.include_router(me_router)
app.include_router(token_router)