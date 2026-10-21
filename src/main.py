from fastapi import FastAPI
from src.routers.register import router as register_router

app = FastAPI()
app.include_router(register_router)
