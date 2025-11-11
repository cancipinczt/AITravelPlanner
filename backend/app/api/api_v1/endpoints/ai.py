from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
import logging
from app.core.ai_client import ai_client
from app.schemas.ai import AIPlanRequest, AIPlanResponse, TravelRequirementsParseRequest, TravelRequirementsParseResponse

logger = logging.getLogger(__name__)

router = APIRouter()

# 修复路由路径：移除重复的/ai前缀
@router.post("/plan", response_model=AIPlanResponse)
async def generate_travel_plan(request: AIPlanRequest) -> AIPlanResponse:
    """
    生成AI旅行计划 - 使用真实的阿里云百炼API
    """
    try:
        # 构建用户输入
        user_input = f"""
目的地：{request.destination}
旅行天数：{request.duration}天
预算：{request.budget}元
同行人数：{request.travelers}人
旅行偏好：{request.preferences}
特殊需求：{request.special_requirements or '无'}
        """.strip()
        
        # 调用AI客户端生成旅行计划
        plan_result = await ai_client.generate_travel_plan(user_input)
        
        return AIPlanResponse(
            itinerary=plan_result["itinerary"],
            budget_usage=plan_result["budget_usage"],
            recommendations=plan_result["recommendations"],
            weather_info=plan_result["weather_info"],
            status=plan_result["status"],
            error=plan_result.get("error")
        )
        
    except Exception as e:
        logger.error(f"生成旅行计划失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"生成旅行计划失败: {str(e)}")

@router.get("/recommendations")
async def get_recommendations(destination: str, preferences: str = "") -> Dict[str, Any]:
    """
    获取景点推荐
    """
    try:
        pref_list = [p.strip() for p in preferences.split(",")] if preferences else []
        recommendations = await ai_client.get_poi_recommendations(destination, pref_list)
        
        return {
            "destination": destination,
            "recommendations": recommendations,
            "count": len(recommendations)
        }
        
    except Exception as e:
        logger.error(f"获取推荐失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"获取推荐失败: {str(e)}")

@router.post("/optimize")
async def optimize_plan(plan_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    优化旅行计划（待实现）
    """
    return {
        "message": "优化功能待实现",
        "optimized_plan": plan_data
    }

@router.get("/weather/{location}")
async def get_weather(location: str) -> Dict[str, Any]:
    """
    获取天气信息（模拟实现）
    """
    return {
        "location": location,
        "temperature": "25°C",
        "weather": "晴朗",
        "humidity": "60%",
        "forecast": "未来几天天气良好"
    }

@router.post("/parse-requirements", response_model=TravelRequirementsParseResponse)
async def parse_travel_requirements(request: TravelRequirementsParseRequest) -> TravelRequirementsParseResponse:
    """
    解析用户输入的旅行需求，提取目的地、天数、预算、同行人数
    """
    try:
        # 调用AI客户端解析旅行需求
        parse_result = await ai_client.parse_travel_requirements(request.travel_requirements)
        
        if parse_result["status"] == "success":
            return TravelRequirementsParseResponse(
                destination=parse_result["destination"],
                duration=parse_result["duration"],
                budget=parse_result["budget"],
                travelers=parse_result["travelers"],
                status="success"
            )
        else:
            raise HTTPException(status_code=400, detail=parse_result.get("error", "解析旅行需求失败"))
            
    except Exception as e:
        logger.error(f"解析旅行需求失败: {str(e)}")
        raise HTTPException(status_code=500, detail=f"解析旅行需求失败: {str(e)}")