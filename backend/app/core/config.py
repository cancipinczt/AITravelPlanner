from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "AI旅行规划师"
    API_V1_STR: str = "/api/v1"
    
    # 数据库配置
    # DATABASE_URL: str
    
    # Supabase配置
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # 阿里云配置
    ALIYUN_AI_KEY: str
    # ALIYUN_OSS_KEY: str
    
    # 安全配置
    SECRET_KEY: str
    JWT_SECRET: str
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # 新增：前端URL配置
    FRONTEND_URL: str
    
    # Redis配置
    REDIS_URL: str
    
    class Config:
        case_sensitive = True
        # 使用绝对路径确保可靠性
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env.dev")
        # 允许额外字段，避免验证错误
        extra = "ignore"

settings = Settings()