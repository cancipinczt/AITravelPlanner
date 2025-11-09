import httpx
import json
from typing import Dict, Any, Optional
from app.core.config import settings

class AIClient:
    """AI服务客户端，专注于阿里云AI服务"""
    
    def __init__(self):
        self.aliyun_ai_key = settings.ALIYUN_AI_KEY
        self.base_url = "https://dashscope.aliyuncs.com/api/v1/services/aigc/text-generation/generation"
    
    async def generate_travel_plan(self, user_input: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """生成旅行计划 - 使用阿里云AI服务"""
        try:
            # 构建请求数据
            request_data = {
                "model": "qwen-turbo",
                "input": {
                    "messages": [
                        {
                            "role": "system",
                            "content": "你是一个专业的旅行规划师，请根据用户需求生成详细的旅行计划，包括行程安排、景点推荐、预算建议等。"
                        },
                        {
                            "role": "user", 
                            "content": f"用户需求：{user_input}，偏好：{preferences}"
                        }
                    ]
                },
                "parameters": {
                    "result_format": "message"
                }
            }
            
            # 调用阿里云AI API（模拟实现）
            headers = {
                "Authorization": f"Bearer {self.aliyun_ai_key}",
                "Content-Type": "application/json"
            }
            
            # 模拟响应（实际开发时需要真实调用）
            plan = {
                "destination": "北京",
                "duration_days": 5,
                "budget": 3000,
                "itinerary": [
                    {
                        "day": 1,
                        "date": "2024-06-01",
                        "activities": [
                            {"time": "09:00", "activity": "抵达北京首都机场", "location": "首都机场"},
                            {"time": "11:00", "activity": "入住酒店", "location": "王府井附近酒店"},
                            {"time": "14:00", "activity": "参观天安门广场", "location": "天安门广场"},
                            {"time": "16:00", "activity": "游览故宫博物院", "location": "故宫"}
                        ]
                    }
                ],
                "recommendations": [
                    {
                        "name": "故宫博物院",
                        "type": "历史文化",
                        "location": "北京市东城区景山前街4号",
                        "description": "中国明清两代的皇家宫殿，世界文化遗产"
                    }
                ]
            }
            
            return {"success": True, "data": plan}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    async def get_poi_recommendations(self, destination: str, preferences: Dict[str, Any]) -> Dict[str, Any]:
        """获取景点推荐 - 使用阿里云AI"""
        try:
            # 模拟AI推荐结果
            recommendations = [
                {
                    "name": "故宫博物院",
                    "type": "历史文化",
                    "location": "北京市东城区景山前街4号",
                    "rating": 4.8,
                    "description": "中国明清两代的皇家宫殿，世界文化遗产",
                    "recommended_time": "3-4小时"
                }
            ]
            
            return {"success": True, "data": recommendations}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# 创建全局AI客户端实例
ai_client = AIClient()