from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user
from app.schemas.trip import AIPlanRequest, AIPlanResponse

router = APIRouter()

# AI规划API - 按照需求文档4.1.6规范

@router.post("/ai/plan", response_model=AIPlanResponse)
async def ai_travel_plan(
    plan_request: AIPlanRequest,
    current_user = Depends(get_current_user)
):
    """AI旅行规划"""
    # TODO: 集成阿里云百炼AI服务
    # 这里先返回模拟数据用于测试
    
    return AIPlanResponse(
        itinerary=[],
        total_cost_estimate=plan_request.budget * 0.8,  # 模拟80%预算使用
        recommendations=[
            {
                "type": "attraction",
                "name": "示例景点",
                "reason": "基于您的偏好推荐"
            }
        ],
        weather_info={
            "temperature": "25°C",
            "condition": "晴朗"
        }
    )

@router.post("/ai/recommendations")
async def ai_recommendations():
    """景点/餐厅推荐"""
    # TODO: 实现AI推荐逻辑
    return {"message": "AI推荐功能待实现"}

@router.post("/ai/optimize")
async def ai_optimize():
    """行程优化建议"""
    # TODO: 实现行程优化逻辑
    return {"message": "行程优化功能待实现"}

@router.get("/ai/weather/{location}")
async def get_weather(location: str):
    """天气信息获取"""
    # TODO: 集成天气API
    return {
        "location": location,
        "temperature": "25°C",
        "condition": "晴朗",
        "forecast": "未来几天天气良好"
    }