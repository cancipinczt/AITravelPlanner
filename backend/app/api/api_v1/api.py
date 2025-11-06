from fastapi import APIRouter
from app.api.api_v1.endpoints import health, travel, auth, user

api_router = APIRouter()

# 包含健康检查路由
api_router.include_router(health.router, tags=["health"])

# 包含旅行规划路由
api_router.include_router(travel.router, prefix="/travel", tags=["travel"])

# 包含用户认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 包含用户管理路由
api_router.include_router(user.router, prefix="/user", tags=["user"])