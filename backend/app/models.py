from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from app.core.database import Base
import uuid

class User(Base):
    __tablename__ = "users"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True)
    password_hash = Column(String(255))
    username = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class TravelPlan(Base):
    __tablename__ = "travel_plans"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    title = Column(String(200))
    destination = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Integer)
    travelers_count = Column(Integer)
    preferences = Column(Text)
    itinerary = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    status = Column(String(20), default="draft")

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    travel_plan_id = Column(UUID(as_uuid=True), index=True)
    day_number = Column(Integer)
    activities = Column(Text)
    accommodation = Column(String(100))
    transportation = Column(String(100))

# 新增费用记录表
class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), index=True)
    category = Column(String(50))
    amount = Column(Integer)
    description = Column(Text)
    date = Column(DateTime)
    created_at = Column(DateTime(timezone=True), server_default=func.now())