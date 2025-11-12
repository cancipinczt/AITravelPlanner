from fastapi import APIRouter, UploadFile, File, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.responses import StreamingResponse
import json
import asyncio
from typing import AsyncGenerator
from app.core.speech_client import speech_client
from app.core.auth import get_current_user
from app.schemas.speech import SpeechRecognitionResponse, RealTimeTranscriptionResponse
import wave
import io

router = APIRouter()

@router.websocket("/transcribe")
async def transcribe_realtime(websocket: WebSocket):
    """
    实时语音转录接口 - 真实科大讯飞API调用
    - 使用WebSocket进行实时音频流传输
    - 实时返回转录结果
    """
    await websocket.accept()
    
    try:
        # 使用事件来控制音频流生成
        stream_active = True
        
        # 接收音频数据流 - 修复连接断开后的处理
        async def audio_stream_generator():
            nonlocal stream_active
            try:
                # 实时接收音频数据，而不是一次性接收完整音频
                while stream_active:
                    try:
                        # 接收音频数据块，设置较短的超时时间
                        message = await asyncio.wait_for(websocket.receive(), timeout=0.5)
                        
                        if message["type"] == "websocket.receive":
                            if "bytes" in message:
                                audio_chunk = message["bytes"]
                                if len(audio_chunk) > 0:
                                    print(f"接收到实时音频块，大小: {len(audio_chunk)} bytes")
                                    yield audio_chunk
                            elif "text" in message:
                                # 处理文本消息（如结束标记）
                                text_data = message["text"]
                                if text_data == "end":
                                    print("收到结束标记")
                                    stream_active = False
                                    break
                    
                    except asyncio.TimeoutError:
                        # 超时继续等待，不中断循环
                        continue
                    except WebSocketDisconnect:
                        print("客户端断开连接")
                        stream_active = False
                        break
                    except Exception as e:
                        print(f"音频流接收错误: {e}")
                        stream_active = False
                        break
                        
            except Exception as e:
                print(f"音频流生成错误: {e}")
                raise
        
        # 调用科大讯飞实时转录（真实API）
        transcription_generator = speech_client.transcribe_realtime(audio_stream_generator())
        
        # 正确处理异步生成器
        async for result in transcription_generator:
            print(f"收到转录结果: {result}")
            
            if not result["success"]:
                # 发送错误信息
                error_response = {
                    "success": False,
                    "error": result["error"]
                }
                try:
                    await websocket.send_text(json.dumps(error_response))
                except:
                    pass  # 连接可能已经断开
                break
            
            # 发送转录结果
            response = {
                "success": True,
                "transcript": result["transcript"],
                "is_final": result.get("is_final", False),
                "confidence": result["confidence"]
            }
            try:
                await websocket.send_text(json.dumps(response))
            except:
                print("发送转录结果失败，连接可能已断开")
                break
            
            # 如果是最终结果，结束连接
            if result.get("is_final", False) and result.get("transcript", "").strip() != "":
                print("收到最终结果，结束连接")
                break
                
    except WebSocketDisconnect:
        print("WebSocket连接断开")
        pass
    except Exception as e:
        print(f"实时转录异常: {e}")
        error_result = {
            "success": False,
            "error": f"实时转录异常: {str(e)}"
        }
        try:
            await websocket.send_text(json.dumps(error_result))
        except:
            pass  # 连接可能已经断开