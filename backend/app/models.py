from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean
from sqlalchemy.sql import func
from app.core.database import Base

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    email = Column(String(100), unique=True, index=True)
    hashed_password = Column(String(100))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    is_active = Column(Boolean, default=True)

class TravelPlan(Base):
    __tablename__ = "travel_plans"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, index=True)
    destination = Column(String(100))
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    budget = Column(Integer)
    preferences = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    status = Column(String(20), default="draft")

class Itinerary(Base):
    __tablename__ = "itineraries"
    
    id = Column(Integer, primary_key=True, index=True)
    travel_plan_id = Column(Integer, index=True)
    day_number = Column(Integer)
    activities = Column(Text)
    accommodation = Column(String(100))
    transportation = Column(String(100))