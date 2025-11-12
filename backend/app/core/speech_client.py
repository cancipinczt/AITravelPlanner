import asyncio
import base64
import hashlib
import hmac
import json
import time
import websockets
from typing import Dict, Any, AsyncGenerator
from urllib.parse import quote
from app.core.config import settings

class IFlyTekSpeechClient:
    """科大讯飞语音识别客户端 - 修正认证和音频处理"""
    
    def __init__(self):
        self.app_id = settings.SPEECH_APP_ID
        self.api_key = settings.SPEECH_API_KEY
        
        # 科大讯飞实时语音转写API端点 - 使用wss协议
        self.realtime_api_url = "wss://rtasr.xfyun.cn/v1/ws"
    
    def _generate_auth_url(self) -> str:
        """生成科大讯飞实时语音转写鉴权URL - 修正认证方式"""
        # 生成时间戳
        timestamp = str(int(time.time()))
        
        # 按照官方Demo的方式生成签名
        # 1. 生成baseString: MD5(app_id + timestamp)
        tt = (self.app_id + timestamp).encode('utf-8')
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding='utf-8')
        
        # 2. 使用HMAC-SHA1签名
        apiKey = self.api_key.encode('utf-8')
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, 'utf-8')
        
        # 3. 生成URL参数
        auth_url = f"{self.realtime_api_url}?appid={self.app_id}&ts={timestamp}&signa={quote(signa)}"
        return auth_url
    
    def _extract_text_from_iflytek_result(self, data: str) -> str:
        """从科大讯飞API结果中提取纯文本内容"""
        try:
            # 解析JSON数据
            result_data = json.loads(data)
            print(f"原始API响应: {data}")  # 添加调试日志
            
            # 提取文本内容
            text_parts = []
            
            # 检查是否有中文结果
            if "cn" in result_data and "st" in result_data["cn"]:
                st_data = result_data["cn"]["st"]
                
                # 处理rt数组中的每个结果段
                if "rt" in st_data:
                    for rt_item in st_data["rt"]:
                        if "ws" in rt_item:
                            for ws_item in rt_item["ws"]:
                                if "cw" in ws_item:
                                    for cw_item in ws_item["cw"]:
                                        if "w" in cw_item:
                                            text_parts.append(cw_item["w"])
            
            # 如果没有提取到文本，尝试其他格式
            if not text_parts:
                # 尝试直接提取文本字段
                if "text" in result_data:
                    text_parts.append(result_data["text"])
                elif "transcript" in result_data:
                    text_parts.append(result_data["transcript"])
            
            # 合并文本并返回
            if text_parts:
                extracted_text = "".join(text_parts)
                print(f"提取的文本: '{extracted_text}'")  # 添加调试日志
                return extracted_text
            else:
                # 如果没有提取到文本，返回原始数据用于调试
                print("未提取到文本，返回原始数据")  # 添加调试日志
                return data
                
        except Exception as e:
            print(f"解析科大讯飞结果错误: {e}")
            # 解析失败时返回原始数据
            return data

    async def transcribe_realtime(self, audio_stream: AsyncGenerator[bytes, None]) -> AsyncGenerator[Dict[str, Any], None]:
        """实时语音转写 - 优化连接管理和错误处理"""
        try:
            # 生成鉴权URL
            auth_url = self._generate_auth_url()
            print(f"连接科大讯飞API: {auth_url}")
            
            # 设置更长的超时时间和ping间隔
            async with websockets.connect(
                auth_url, 
                ping_timeout=20, 
                close_timeout=20,
                ping_interval=10  # 添加ping间隔保持连接活跃
            ) as websocket:
                print("科大讯飞API连接成功")
                
                # 等待握手响应
                try:
                    handshake_response = await asyncio.wait_for(websocket.recv(), timeout=5.0)
                    print(f"握手响应: {handshake_response}")
                    
                    handshake_result = json.loads(handshake_response)
                    if handshake_result.get("action") == "error":
                        error_msg = f"握手失败: {handshake_result.get('code', '未知')} - {handshake_result.get('desc', '未知错误')}"
                        yield {
                            "success": False,
                            "error": error_msg
                        }
                        return
                        
                except asyncio.TimeoutError:
                    print("握手响应超时，继续处理音频")
                
                # 创建发送音频的异步任务
                async def send_audio():
                    """发送音频数据"""
                    audio_chunk_count = 0
                    try:
                        async for audio_chunk in audio_stream:
                            if len(audio_chunk) > 0:
                                audio_chunk_count += 1
                                print(f"发送第{audio_chunk_count}个音频块，大小: {len(audio_chunk)} bytes")
                                
                                # 直接发送原始音频数据
                                try:
                                    await websocket.send(audio_chunk)
                                    print(f"音频数据发送成功 (块{audio_chunk_count})")
                                except websockets.exceptions.ConnectionClosed:
                                    print("发送音频时连接已关闭")
                                    break
                        
                        # 发送结束标记
                        end_tag = '{"end": true}'
                        try:
                            await websocket.send(end_tag)
                            print("结束标记发送成功")
                        except websockets.exceptions.ConnectionClosed:
                            print("发送结束标记时连接已关闭")
                    except Exception as e:
                        print(f"发送音频数据异常: {e}")
                
                # 启动音频发送任务
                send_task = asyncio.create_task(send_audio())
                
                # 直接处理接收结果，而不是创建任务
                while True:
                    try:
                        # 设置较短的超时时间，实现真正的实时响应
                        response = await asyncio.wait_for(websocket.recv(), timeout=1.0)
                        print(f"收到API响应: {response}")
                        
                        result = json.loads(response)
                        
                        # 解析结果
                        if result.get("action") == "started":
                            print("握手成功")
                            continue
                        
                        if result.get("action") == "result":
                            # 解析识别结果
                            data = result.get("data", "")
                            if data:
                                # 提取纯文本内容
                                transcript_text = self._extract_text_from_iflytek_result(data)
                                print(f"识别结果: '{transcript_text}'")
                                
                                # 修复：检查是否为纯标点符号或空内容
                                cleaned_text = transcript_text.strip()
                                if cleaned_text and cleaned_text not in ['.', '。', '!', '！', '?', '？']:
                                    yield {
                                        "success": True,
                                        "transcript": transcript_text,
                                        "is_final": False,
                                        "confidence": 0.9
                                    }
                                else:
                                    print(f"跳过无效转录内容: '{transcript_text}'")
                        
                        if result.get("action") == "end":
                            print("收到结束响应")
                            # 修复：完全跳过结束响应，不发送任何转录结果
                            print("语音转录结束，跳过结束响应")
                            break
                        
                        if result.get("action") == "error":
                            error_msg = f"API错误: {result.get('code', '未知')} - {result.get('desc', '未知错误')}"
                            print(f"API错误: {error_msg}")
                            yield {
                                "success": False,
                                "error": error_msg
                            }
                            break
                        
                        if result.get("action") == "end":
                            print("收到结束响应")
                            # 修复：完全跳过结束响应，不发送任何转录结果
                            print("语音转录结束，跳过结束响应")
                            break
                            
                    except asyncio.TimeoutError:
                        # 没有新结果，继续等待
                        continue
                    except websockets.exceptions.ConnectionClosed:
                        print("科大讯飞WebSocket连接关闭")
                        break
                    except Exception as e:
                        print(f"接收结果异常: {e}")
                        break
                
                # 等待发送任务完成或取消
                if send_task and not send_task.done():
                    send_task.cancel()
                    try:
                        await send_task
                    except asyncio.CancelledError:
                        print("音频发送任务已取消")
            
        except websockets.exceptions.InvalidURI as e:
            yield {
                "success": False,
                "error": f"认证URL无效: {str(e)}"
            }
        except websockets.exceptions.InvalidHandshake as e:
            yield {
                "success": False,
                "error": f"握手失败，请检查API Key和App ID: {str(e)}"
            }
        except Exception as e:
            print(f"实时转录异常: {e}")
            yield {
                "success": False,
                "error": f"实时转录失败: {str(e)}"
            }

# 创建全局语音客户端实例
speech_client = IFlyTekSpeechClient()