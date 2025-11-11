from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime
from decimal import Decimal

# 旅行计划创建请求 - 简化版
class TripCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    destination: str = Field(..., min_length=1, max_length=100)
    budget: Optional[Decimal] = None
    travelers_count: int = Field(default=1, ge=1)
    days: int = Field(..., ge=1, description="旅行天数")
    preference_id: Optional[UUID] = None
    plan: Optional[str] = None

# 旅行计划更新请求 - 简化版
class TripUpdate(BaseModel):
    title: Optional[str] = Field(None, min_length=1, max_length=200)
    destination: Optional[str] = Field(None, min_length=1, max_length=100)
    budget: Optional[Decimal] = None
    travelers_count: Optional[int] = Field(None, ge=1)
    days: Optional[int] = Field(None, ge=1, description="旅行天数")
    preference_id: Optional[UUID] = None
    plan: Optional[str] = None

# 旅行计划简要信息响应 - 用于列表显示
class TripBriefResponse(BaseModel):
    id: UUID
    title: str
    destination: str
    budget: Optional[Decimal] = None
    travelers_count: int
    days: int
    preference_name: Optional[str] = None  # 通过preference_id获取的用户偏好名称
    created_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }

# 旅行计划完整响应 - 简化版
class TripResponse(BaseModel):
    id: UUID
    user_id: UUID
    title: str
    destination: str
    budget: Optional[Decimal] = None
    travelers_count: int
    days: int
    preference_id: Optional[UUID] = None
    plan: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }

# 费用记录 - 保持不变
class ExpenseCreate(BaseModel):
    category: str
    amount: Decimal
    currency: str = "CNY"
    description: Optional[str] = None
    expense_date: datetime
    payment_method: Optional[str] = None
    is_planned: bool = False
    tags: Optional[list[str]] = None

class ExpenseResponse(BaseModel):
    id: UUID
    trip_id: UUID
    category: str
    amount: Decimal
    currency: str
    description: Optional[str] = None
    expense_date: datetime
    payment_method: Optional[str] = None
    is_planned: bool
    tags: Optional[list[str]] = None
    created_at: datetime

    class Config:
        from_attributes = True