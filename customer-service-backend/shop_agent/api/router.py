from fastapi import APIRouter

from shop_agent.api.v1.router import v1_router

api_router = APIRouter()
api_router.include_router(v1_router)

# 如果切换其他版本：
# from shop_agent.api.v2.router import v2_router
# api_router.include_router(v2_router, prefix="/v2")
