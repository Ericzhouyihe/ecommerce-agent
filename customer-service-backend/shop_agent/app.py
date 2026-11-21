from contextlib import asynccontextmanager

from fastapi import FastAPI

from shop_agent.api.dependencies import init_dialogue_engine
from shop_agent.api.v1.chat_router import chat_router
from shop_agent.infrastructure.db.database import close_db_engine, init_db_engine
from shop_agent.infrastructure.http_client import close_http_client, init_http_client


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_http_client()
    init_dialogue_engine()
    init_db_engine()
    yield
    await close_db_engine()
    await close_http_client()


app = FastAPI(lifespan=lifespan)
app.include_router(chat_router)
