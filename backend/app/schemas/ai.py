from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from datetime import date
from decimal import Decimal

class AIPlanRequest(BaseModel):
    """AI规划请求模型"""
    destination: str = Field(..., description="目的地")
    duration: int = Field(..., ge=1, le=30, description="旅行天数")
    budget: Decimal = Field(..., ge=0, description="预算")
    travelers: int = Field(..., ge=1, le=10, description="同行人数")
    preferences: str = Field("", description="旅行偏好")
    special_requirements: Optional[str] = Field(None, description="特殊需求")

class AIPlanResponse(BaseModel):
    """AI规划响应模型"""
    itinerary: str = Field(..., description="行程安排")
    budget_usage: Dict[str, Any] = Field(default_factory=dict, description="预算使用情况")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="推荐信息")
    weather_info: Dict[str, Any] = Field(default_factory=dict, description="天气信息")
    status: str = Field(..., description="状态：success/error")
    error: Optional[str] = Field(None, description="错误信息")

class AIRecommendationRequest(BaseModel):
    """AI推荐请求模型"""
    destination: str = Field(..., description="目的地")
    preferences: str = Field("", description="偏好")

class AIRecommendationResponse(BaseModel):
    """AI推荐响应模型"""
    destination: str = Field(..., description="目的地")
    recommendations: List[Dict[str, Any]] = Field(default_factory=list, description="推荐列表")
    count: int = Field(..., description="推荐数量")

class TravelRequirementsParseRequest(BaseModel):
    """旅行需求解析请求模型"""
    travel_requirements: str = Field(..., description="用户输入的旅行需求文本")

class TravelRequirementsParseResponse(BaseModel):
    """旅行需求解析响应模型"""
    destination: str = Field(..., description="解析出的目的地")
    duration: int = Field(..., description="解析出的旅行天数")
    budget: Decimal = Field(..., description="解析出的预算")
    travelers: int = Field(..., description="解析出的同行人数")
    status: str = Field(..., description="状态：success/error")
    error: Optional[str] = Field(None, description="错误信息")