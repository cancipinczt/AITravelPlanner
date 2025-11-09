from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from uuid import UUID
from datetime import datetime, date, time
from decimal import Decimal

# 旅行计划创建请求
class TripCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=100)
    start_date: date
    end_date: date
    budget: Optional[Decimal] = None
    travelers_count: int = Field(default=1, ge=1)
    travel_style: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

# 旅行计划更新请求
class TripUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    destination: Optional[str] = Field(None, min_length=1, max_length=100)
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    budget: Optional[Decimal] = None
    travelers_count: Optional[int] = Field(None, ge=1)
    travel_style: Optional[str] = None
    preferences: Optional[Dict[str, Any]] = None

# 旅行计划响应
class TripResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    destination: str
    start_date: date
    end_date: date
    budget: Optional[Decimal] = None
    travelers_count: int
    travel_style: Optional[str] = None
    status: str
    preferences: Optional[Dict[str, Any]] = None
    ai_generated_content: Optional[Dict[str, Any]] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }

# 活动安排
class Activity(BaseModel):
    type: str
    time: time
    location: str
    description: str
    duration_minutes: int
    cost_estimate: Optional[Decimal] = None

# 行程详情创建请求
class ItineraryCreate(BaseModel):
    day_number: int = Field(..., ge=1)
    date: date
    activities: List[Activity]
    transportation: Optional[Dict[str, Any]] = None
    accommodation: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None

# 行程详情响应
class ItineraryResponse(BaseModel):
    id: UUID
    trip_id: UUID
    day_number: int
    date: date
    activities: List[Activity]
    transportation: Optional[Dict[str, Any]] = None
    accommodation: Optional[Dict[str, Any]] = None
    notes: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True

# AI规划请求
class AIPlanRequest(BaseModel):
    destination: str
    start_date: date
    end_date: date
    budget: Decimal
    travelers_count: int
    preferences: Optional[Dict[str, Any]] = None
    special_requirements: Optional[str] = None

# AI规划响应
class AIPlanResponse(BaseModel):
    itinerary: List[ItineraryResponse]
    total_cost_estimate: Decimal
    recommendations: List[Dict[str, Any]]
    weather_info: Optional[Dict[str, Any]] = None

# 费用记录
class ExpenseCreate(BaseModel):
    category: str
    amount: Decimal
    currency: str = "CNY"
    description: Optional[str] = None
    expense_date: date
    payment_method: Optional[str] = None
    is_planned: bool = False
    tags: Optional[List[str]] = None

class ExpenseResponse(BaseModel):
    id: UUID
    trip_id: UUID
    category: str
    amount: Decimal
    currency: str
    description: Optional[str] = None
    expense_date: date
    payment_method: Optional[str] = None
    is_planned: bool
    tags: Optional[List[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True

# 景点推荐
class POIRecommendationResponse(BaseModel):
    id: UUID
    trip_id: UUID
    poi_name: str
    poi_type: str
    location: Optional[str] = None
    latitude: Optional[Decimal] = None
    longitude: Optional[Decimal] = None
    rating: Optional[Decimal] = None
    price_range: Optional[str] = None
    description: Optional[str] = None
    recommendation_reason: Optional[str] = None
    is_selected: bool
    created_at: datetime

    class Config:
        from_attributes = True