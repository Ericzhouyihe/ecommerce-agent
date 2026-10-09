from fastapi import APIRouter

from shop_agent.api.v1 import chat_router

v1_router = APIRouter()
v1_router.include_router(chat_router.router)
