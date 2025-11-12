from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # 项目配置
    PROJECT_NAME: str = "AI旅行规划师"
    API_V1_STR: str = "/api/v1"
    
    # Supabase配置
    SUPABASE_URL: str
    SUPABASE_KEY: str
    
    # 阿里云AI配置 - 用于智能行程规划
    ALIYUN_AI_KEY: str
    
    # 地图服务配置 - 用于地图交互界面
    MAP_API_KEY: str
    
    # 语音识别配置 - 科大讯飞实时语音转写API
    SPEECH_APP_ID: str  # 科大讯飞应用ID
    SPEECH_API_KEY: str  # 科大讯飞实时语音转写API Key
    
    # 安全配置
    SECRET_KEY: str
    JWT_SECRET: str
    
    # CORS配置
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost:3000"]

    # 前端URL配置
    FRONTEND_URL: str
        
    class Config:
        case_sensitive = True
        # 使用绝对路径确保可靠性
        env_file = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.dirname(__file__)))), ".env.dev")
        # 允许额外字段，避免验证错误
        extra = "ignore"

settings = Settings()