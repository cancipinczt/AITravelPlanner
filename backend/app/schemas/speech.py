from pydantic import BaseModel
from typing import Optional

class SpeechRecognitionResponse(BaseModel):
    """语音转文本响应模型"""
    success: bool
    transcript: str
    confidence: float
    language: str
    error: Optional[str] = None

class RealTimeTranscriptionResponse(BaseModel):
    """实时语音转录响应模型"""
    success: bool
    transcript: str
    is_final: bool
    confidence: float
    error: Optional[str] = None

class SpeechRecognitionRequest(BaseModel):
    """语音识别请求模型"""
    language: str = "zh_cn"
    audio_format: str = "wav"