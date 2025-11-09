from fastapi import APIRouter
from app.api.api_v1.endpoints import health, travel, auth, user, trips, ai, speech

api_router = APIRouter()

# 包含健康检查路由
api_router.include_router(health.router, tags=["health"])

# 包含旅行规划路由（保留原有接口）
api_router.include_router(travel.router, prefix="/travel", tags=["travel"])

# 包含用户认证路由
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])

# 包含用户管理路由
api_router.include_router(user.router, prefix="/user", tags=["user"])

# 包含新的旅行计划API路由（按照需求文档4.1.3规范）
api_router.include_router(trips.router, prefix="/trips", tags=["trips"])

# 包含AI规划API路由（按照需求文档4.1.6规范）
api_router.include_router(ai.router, prefix="/ai", tags=["ai"])

# 包含语音识别API路由（按照需求文档4.1.5规范）
api_router.include_router(speech.router, prefix="/speech", tags=["speech"])