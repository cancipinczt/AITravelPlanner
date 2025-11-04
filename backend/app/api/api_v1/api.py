from fastapi import APIRouter
from app.api.api_v1.endpoints import health, travel

api_router = APIRouter()

# 包含健康检查路由
api_router.include_router(health.router, tags=["health"])

# 包含旅行规划路由
api_router.include_router(travel.router, prefix="/travel", tags=["travel"])