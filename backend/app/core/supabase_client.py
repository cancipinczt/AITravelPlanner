from supabase import create_client
from app.core.config import settings

# 创建Supabase客户端
supabase = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

def get_supabase_client():
    """获取Supabase客户端实例"""
    return supabase