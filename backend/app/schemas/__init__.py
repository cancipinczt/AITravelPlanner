from .auth import *
from .speech import *
from .trip import *
from .ai import AIPlanRequest, AIPlanResponse, AIRecommendationRequest, AIRecommendationResponse

__all__ = [
    # 从auth.py导出
    "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    
    # 从speech.py导出
    "SpeechRequest", "SpeechResponse", "VoiceRecordCreate", "VoiceRecordResponse",
    
    # 从trip.py导出（移除AI相关模型）
    "TripCreate", "TripUpdate", "TripResponse", "Activity", "ItineraryCreate", 
    "ItineraryResponse", "ExpenseCreate", "ExpenseResponse", "POIRecommendationResponse",
    
    # 从ai.py导出
    "AIPlanRequest", "AIPlanResponse", "AIRecommendationRequest", "AIRecommendationResponse"
]