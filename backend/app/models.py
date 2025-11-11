from sqlalchemy import Column, Integer, String, DateTime, Text, Boolean, DECIMAL
from sqlalchemy.dialects.postgresql import UUID
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

# 按照简化后的旅行计划表结构
class Trip(Base):
    __tablename__ = "trips"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    user_id = Column(UUID(as_uuid=True), index=True)
    title = Column(String(200), nullable=False)
    destination = Column(String(100), nullable=False)
    budget = Column(DECIMAL(10, 2))
    travelers_count = Column(Integer, default=1)
    days = Column(Integer, nullable=False)
    preference_id = Column(UUID(as_uuid=True))
    plan = Column(Text)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

# 费用记录表 - 保持不变
class Expense(Base):
    __tablename__ = "expenses"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    trip_id = Column(UUID(as_uuid=True), index=True)
    category = Column(String(50), nullable=False)
    amount = Column(DECIMAL(10, 2), nullable=False)
    currency = Column(String(3), default='CNY')
    description = Column(Text)
    expense_date = Column(DateTime, nullable=False)
    payment_method = Column(String(50))
    receipt_url = Column(String(500))
    is_planned = Column(Boolean, default=False)
    tags = Column(Text)  # 改为Text类型存储标签
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())