import os
import json
import logging
from typing import Dict, Any, List, Optional
from dashscope import Generation
import dashscope
from app.core.config import settings

logger = logging.getLogger(__name__)

class AIClient:
    def __init__(self):
        # 配置API密钥 - 使用正确的配置名称
        self.api_key = settings.ALIYUN_AI_KEY
        if not self.api_key:
            logger.warning("ALIYUN_AI_KEY not found in environment variables")
        
        # 配置模型
        self.model = "qwen-plus-2025-07-28"  # 使用qwen-turbo模型，支持长文本生成
        
        # 系统提示词 - 专门针对旅行规划
        self.system_prompt = """你是一个专业的旅行规划专家。请根据用户的需求生成详细、个性化的旅行计划。

旅行计划需要包含以下完整信息：
1. 行程安排：按天详细规划，包括交通、住宿、景点、餐饮等
2. 预算分配：详细列出各项费用预算
3. 景点推荐：根据用户偏好推荐合适的景点
4. 餐饮推荐：推荐当地特色美食
5. 交通建议：提供最佳交通方式和路线
6. 注意事项：旅行安全、文化差异、天气等提醒

请确保计划合理、实用，并充分考虑用户的预算、时间、偏好等约束条件。"""

    async def generate_travel_plan(self, user_input: str) -> Dict[str, Any]:
        """
        使用阿里云百炼平台生成旅行计划
        """
        try:
            if not self.api_key:
                raise ValueError("ALIYUN_AI_KEY is not configured")
            
            # 构建用户消息
            messages = [
                {'role': 'system', 'content': self.system_prompt},
                {'role': 'user', 'content': f"请为以下旅行需求生成详细的旅行计划：\n\n{user_input}"}
            ]
            
            # 调用阿里云百炼API
            response = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message"
            )
            
            if response.status_code == 200:
                # 解析AI返回的内容
                ai_response = response.output.choices[0].message.content
                
                # 尝试解析JSON格式的响应，如果失败则使用原始文本
                try:
                    plan_data = json.loads(ai_response)
                except json.JSONDecodeError:
                    # 如果AI返回的不是标准JSON，使用原始文本并创建结构化数据
                    # 修复：确保返回正确的数据类型
                    plan_data = {
                        "itinerary": ai_response,
                        "budget_usage": {},  # 修复：改为空字典
                        "recommendations": [],  # 修复：改为空列表
                        "weather_info": {},  # 修复：改为空字典
                        "status": "success",
                        "raw_response": ai_response
                    }
                
                # 确保返回标准格式
                return {
                    "itinerary": plan_data.get("itinerary", ai_response),
                    "budget_usage": plan_data.get("budget_usage", {}),
                    "recommendations": plan_data.get("recommendations", []),
                    "weather_info": plan_data.get("weather_info", {}),
                    "status": "success"
                }
                
            else:
                logger.error(f"AI API调用失败: {response.status_code} - {response.message}")
                return {
                    "itinerary": "AI服务暂时不可用，请稍后重试",
                    "budget_usage": {},
                    "recommendations": [],
                    "weather_info": {},
                    "status": "error",
                    "error": f"API调用失败: {response.message}"
                }
                
        except Exception as e:
            logger.error(f"生成旅行计划时发生错误: {str(e)}")
            return {
                "itinerary": "生成旅行计划时发生错误",
                "budget_usage": {},
                "recommendations": [],
                "weather_info": {},
                "status": "error",
                "error": str(e)
            }

    async def get_poi_recommendations(self, destination: str, preferences: List[str]) -> List[Dict[str, Any]]:
        """
        获取景点推荐（简化实现）
        """
        try:
            # 构建推荐请求
            prompt = f"为目的地{destination}推荐景点，用户偏好：{', '.join(preferences)}"
            
            messages = [
                {'role': 'system', 'content': '你是一个旅游推荐专家，请简洁明了地推荐景点'},
                {'role': 'user', 'content': prompt}
            ]
            
            response = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message"
            )
            
            if response.status_code == 200:
                recommendations = response.output.choices[0].message.content
                # 简化处理，返回包含推荐文本的结果
                return [{"name": destination, "description": recommendations, "type": "attraction"}]
            else:
                return []
                
        except Exception as e:
            logger.error(f"获取景点推荐失败: {str(e)}")
            return []

    async def parse_travel_requirements(self, travel_requirements: str) -> Dict[str, Any]:
        """
        使用大模型解析用户输入的旅行需求
        """
        try:
            if not self.api_key:
                raise ValueError("ALIYUN_AI_KEY is not configured")
            
            # 构建解析提示词
            parse_prompt = f"""
请从以下用户输入的旅行需求中准确提取出目的地、旅行天数、预算和同行人数四个关键信息：

用户输入：{travel_requirements}

请严格按照以下JSON格式返回结果，不要包含任何其他文本：
{{
    "destination": "提取出的目的地，如：日本东京",
    "duration": 提取出的天数（整数），
    "budget": 提取出的预算（数字），
    "travelers": 提取出的同行人数（整数）
}}

提取规则：
1. 目的地：提取具体的地名，如"日本东京"而不是"我想去日本东京玩7天"
2. 天数：提取天数数字，如"7天"提取为7
3. 预算：提取预算金额，如"15000元"提取为15000
4. 同行人数：提取人数数字，如"3人同行"提取为3

如果某个信息无法提取，请使用合理的默认值：
- 天数默认7天
- 预算默认10000元
- 同行人数默认2人
- 目的地必须提取，如果无法提取则返回错误
"""

            messages = [
                {'role': 'system', 'content': '你是一个专业的旅行需求解析助手，请准确提取旅行需求中的关键信息。'},
                {'role': 'user', 'content': parse_prompt}
            ]
            
            # 调用阿里云百炼API
            response = Generation.call(
                api_key=self.api_key,
                model=self.model,
                messages=messages,
                result_format="message"
            )
            
            if response.status_code == 200:
                ai_response = response.output.choices[0].message.content
                
                # 解析JSON响应
                try:
                    parsed_data = json.loads(ai_response)
                    
                    # 验证必需字段
                    if not parsed_data.get("destination"):
                        raise ValueError("无法从用户输入中提取目的地")
                    
                    # 设置默认值
                    duration = parsed_data.get("duration", 7)
                    budget = parsed_data.get("budget", 10000)
                    travelers = parsed_data.get("travelers", 2)
                    
                    return {
                        "destination": parsed_data["destination"],
                        "duration": int(duration),
                        "budget": float(budget),
                        "travelers": int(travelers),
                        "status": "success"
                    }
                    
                except (json.JSONDecodeError, KeyError, ValueError) as e:
                    logger.error(f"解析AI响应失败: {str(e)}")
                    return {
                        "destination": "",
                        "duration": 7,
                        "budget": 10000,
                        "travelers": 2,
                        "status": "error",
                        "error": f"解析响应失败: {str(e)}"
                    }
                
            else:
                logger.error(f"AI API调用失败: {response.status_code} - {response.message}")
                return {
                    "destination": "",
                    "duration": 7,
                    "budget": 10000,
                    "travelers": 2,
                    "status": "error",
                    "error": f"API调用失败: {response.message}"
                }
                
        except Exception as e:
            logger.error(f"解析旅行需求时发生错误: {str(e)}")
            return {
                "destination": "",
                "duration": 7,
                "budget": 10000,
                "travelers": 2,
                "status": "error",
                "error": str(e)
            }

# 创建全局AI客户端实例
ai_client = AIClient()