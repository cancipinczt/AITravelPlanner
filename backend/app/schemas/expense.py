from pydantic import BaseModel, Field
from typing import Optional
from uuid import UUID
from datetime import datetime, date
from decimal import Decimal

# 费用记录创建请求 - 按照需求文档5.1.4规范
class ExpenseCreate(BaseModel):
    amount: Decimal = Field(..., gt=0, description="金额")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    expense_date: date = Field(..., description="消费日期")

# 费用记录更新请求 - 按照需求文档5.1.4规范
class ExpenseUpdate(BaseModel):
    amount: Optional[Decimal] = Field(None, gt=0, description="金额")
    description: Optional[str] = Field(None, max_length=500, description="描述")
    expense_date: Optional[date] = Field(None, description="消费日期")

# 费用记录响应 - 按照需求文档5.1.4规范
class ExpenseResponse(BaseModel):
    id: UUID
    trip_id: UUID
    amount: Decimal
    description: Optional[str] = None
    expense_date: date
    created_at: datetime
    updated_at: Optional[datetime] = None

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None,
            date: lambda v: v.isoformat() if v else None,
            Decimal: lambda v: float(v) if v else None
        }

# 费用统计响应模型
class ExpenseSummaryResponse(BaseModel):
    total_amount: float = Field(..., description="总金额")
    expense_count: int = Field(..., description="费用记录数量")

    class Config:
        from_attributes = True