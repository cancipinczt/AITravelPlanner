from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, DECIMAL, Date, Time
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.sql import func
from sqlalchemy.ext.declarative import declarative_base
import uuid

# 直接在models.py中定义Base类
Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    username = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

# 按照需求文档5.1.3规范更新旅行计划表
class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    title = Column(String(200), nullable=False)
    destination = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=False)
    budget = Column(DECIMAL(10, 2))
    travelers_count = Column(Integer, default=1)
    travel_style = Column(String(50))
    status = Column(String(20), default='draft')
    preferences = Column(JSONB)
    ai_generated_content = Column(JSONB)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 按照需求文档5.1.4规范更新行程详情表
class TripItinerary(Base):
    __tablename__ = "trip_itineraries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), index=True)
    day_number = Column(Integer, nullable=False)
    date = Column(Date, nullable=False)
    activities = Column(JSONB)  # 活动安排数组
    transportation = Column(JSONB)  # 交通安排
    accommodation = Column(JSONB)  # 住宿信息
    notes = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 按照需求文档5.1.5规范更新费用记录表
class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), index=True)
    category = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='CNY')
    description = Column(Text)
    expense_date = Column(Date, nullable=False)
    payment_method = Column(String(50))
    receipt_url = Column(String(500))
    is_planned = Column(Boolean, default=False)
    tags = Column(JSONB)  # 标签数组
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 按照需求文档5.1.6规范创建景点推荐表
class POIRecommendation(Base):
    __tablename__ = "poi_recommendations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), index=True)
    poi_name = Column(String(200), nullable=False)
    poi_type = Column(String(50), nullable=False)
    location = Column(String(100))
    latitude = Column(DECIMAL(10, 8))
    longitude = Column(DECIMAL(11, 8))
    rating = Column(DECIMAL(3, 2))
    price_range = Column(String(20))
    description = Column(Text)
    recommendation_reason = Column(Text)
    is_selected = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

# 按照需求文档5.1.7规范创建语音记录表
class VoiceRecord(Base):
    __tablename__ = "voice_records"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    trip_id = Column(UUID(as_uuid=True), index=True)
    audio_url = Column(String(500), nullable=False)
    transcribed_text = Column(Text)
    duration_seconds = Column(Integer)
    language = Column(String(10), default='zh-CN')
    purpose = Column(String(50))
    created_at = Column(DateTime(timezone=True), server_default=func.now())