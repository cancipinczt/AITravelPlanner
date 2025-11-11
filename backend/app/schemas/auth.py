from pydantic import BaseModel
from typing import Optional, List
from uuid import UUID
from datetime import datetime

class UserCreate(BaseModel):
    username: str
    password: str

class UserLogin(BaseModel):
    username: str
    password: str

class UserResponse(BaseModel):
    id: UUID
    username: str
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    is_active: Optional[bool] = True
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

class Token(BaseModel):
    access_token: str
    token_type: str
    user: UserResponse

class TokenData(BaseModel):
    username: Optional[str] = None

# 用户偏好相关模型 - 修改为支持多个偏好
class UserPreferenceCreate(BaseModel):
    name: str  # 新增：偏好名称
    travel_preferences: Optional[str] = None
    special_requirements: Optional[str] = None

class UserPreferenceUpdate(BaseModel):
    name: Optional[str] = None  # 新增：偏好名称
    travel_preferences: Optional[str] = None
    special_requirements: Optional[str] = None

class UserPreferenceResponse(BaseModel):
    id: UUID
    user_id: UUID
    name: str  # 新增：偏好名称
    travel_preferences: Optional[str] = None
    special_requirements: Optional[str] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    
    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat() if v else None
        }

# 新增：用户偏好列表响应模型
class UserPreferenceListResponse(BaseModel):
    preferences: List[UserPreferenceResponse]
    
    class Config:
        from_attributes = True