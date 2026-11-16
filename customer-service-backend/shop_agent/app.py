from contextlib import asynccontextmanager

from fastapi import FastAPI

from shop_agent.api.dependencies import init_dialogue_engine
from shop_agent.api.router import api_router
from shop_agent.infrastructure.db.database import close_db
from shop_agent.infrastructure.http_client import close_http_client, init_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 启动:初始化 HTTP 客户端、装配对话引擎(数据库引擎在 import 时已创建)
    init_http_client()
    init_dialogue_engine()
    yield
    # 关闭:释放连接池
    await close_db()
    await close_http_client()


app = FastAPI(lifespan=lifespan)
app.include_router(api_router, prefix="/api")
