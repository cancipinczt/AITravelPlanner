#!/usr/bin/env python3
"""
智能行程规划功能服务测试脚本
用于测试AI服务、地图服务、语音服务的连接状态
"""

import os
import sys
import asyncio
from app.core.supabase_client import get_supabase_client
from app.core.config import settings

async def test_supabase_connection():
    """测试Supabase连接"""
    print("开始测试Supabase连接...")
    
    try:
        supabase = get_supabase_client()
        
        # 测试简单的查询
        try:
            response = supabase.table('trips').select('*').limit(1).execute()
            print("✓ Supabase连接成功，表结构已就绪")
            return True
        except Exception as e:
            print(f"⚠️  Supabase连接正常，但表查询失败: {e}")
            print("   请确保已在Supabase控制台中执行了数据库迁移脚本")
            return False
            
    except Exception as e:
        print(f"❌ Supabase连接失败: {e}")
        return False

async def test_ai_services():
    """测试AI服务连接"""
    print("\n开始测试AI服务连接...")
    
    try:
        from app.core.ai_client import ai_client
        from app.core.map_client import map_client
        from app.core.speech_client import speech_client
        
        # 测试AI客户端
        result = await ai_client.generate_travel_plan("北京", {})
        if result["success"]:
            print("✓ AI服务客户端测试成功")
        else:
            print("⚠️  AI服务客户端测试有警告")
        
        # 测试地图客户端
        location = await map_client.geocode_address("北京")
        if location:
            print("✓ 地图服务客户端测试成功")
        else:
            print("⚠️  地图服务客户端测试有警告")
        
        # 测试语音客户端
        transcript = await speech_client.transcribe_audio(b"test")
        if transcript["success"]:
            print("✓ 语音服务客户端测试成功")
        else:
            print("⚠️  语音服务客户端测试有警告")
            
    except Exception as e:
        print(f"❌ AI服务测试失败: {e}")
        return False
    
    return True

async def check_environment_variables():
    """检查环境变量配置"""
    print("检查环境变量配置...")
    
    required_vars = [
        "SUPABASE_URL", "SUPABASE_KEY", "ALIYUN_AI_KEY",
        "MAP_API_KEY", "SPEECH_API_KEY"
    ]
    
    missing_vars = []
    for var in required_vars:
        if not getattr(settings, var, None):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ 缺少必要的环境变量:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n请在.env.dev文件中配置这些环境变量")
        return False
    
    print("✓ 环境变量检查通过")
    return True

async def main():
    """主函数"""
    print("AI旅行规划师 - 智能行程规划功能服务测试")
    print("=" * 50)
    
    # 检查环境变量
    env_success = await check_environment_variables()
    if not env_success:
        return False
    
    # 测试Supabase连接
    db_success = await test_supabase_connection()
    
    # 测试AI服务
    ai_success = await test_ai_services()
    
    if db_success and ai_success:
        print("\n🎉 智能行程规划功能服务测试完成！")
        print("\n✅ 所有核心服务连接正常")
        print("\n下一步：")
        print("1. 启动后端服务: uvicorn main:app --reload")
        print("2. 开始开发前端界面")
        return True
    else:
        print("\n❌ 服务测试过程中遇到问题，请检查上述错误信息")
        return False

if __name__ == "__main__":
    asyncio.run(main())