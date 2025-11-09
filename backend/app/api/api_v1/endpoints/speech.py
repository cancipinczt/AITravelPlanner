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

@router.post("/recognize", response_model=SpeechRecognitionResponse)
async def recognize_speech(
    audio_file: UploadFile = File(...),
    language: str = "zh_cn",
    current_user: dict = Depends(get_current_user)
):
    """
    语音转文本接口
    - 接收音频文件，返回识别结果
    - 支持多种音频格式
    """
    # 验证文件类型
    if not audio_file.content_type.startswith('audio/'):
        raise HTTPException(
            status_code=400, 
            detail="请上传音频文件"
        )
    
    try:
        # 读取音频文件内容
        audio_data = await audio_file.read()
        
        # 调用科大讯飞语音识别
        result = await speech_client.recognize_speech(audio_data, language)
        
        if not result["success"]:
            raise HTTPException(
                status_code=500, 
                detail=result["error"]
            )
        
        return SpeechRecognitionResponse(
            success=True,
            transcript=result["transcript"],
            confidence=result["confidence"],
            language=language
        )
        
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"语音识别处理失败: {str(e)}"
        )

@router.websocket("/transcribe")
async def transcribe_realtime(websocket: WebSocket):
    """
    实时语音转录接口 - 真实科大讯飞API调用
    - 使用WebSocket进行实时音频流传输
    - 实时返回转录结果
    """
    await websocket.accept()
    
    try:
        # 接收音频数据流 - 改为真正的实时流处理
        async def audio_stream_generator():
            try:
                # 实时接收音频数据，而不是一次性接收完整音频
                while True:
                    # 接收音频数据块
                    message = await websocket.receive()
                    
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
                                break
                    
            except WebSocketDisconnect:
                print("客户端断开连接")
                pass
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
                await websocket.send_text(json.dumps(error_response))
                break
            
            # 发送转录结果
            response = {
                "success": True,
                "transcript": result["transcript"],
                "is_final": result.get("is_final", False),
                "confidence": result["confidence"]
            }
            await websocket.send_text(json.dumps(response))
            
            # 如果是最终结果，结束连接
            if result.get("is_final", False):
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