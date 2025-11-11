from .auth import *
from .speech import *
from .trip import *
from .ai import AIPlanRequest, AIPlanResponse, AIRecommendationRequest, AIRecommendationResponse
from .expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseSummaryResponse  # 添加expense导入

__all__ = [
    # 从auth.py导出
    "UserCreate", "UserLogin", "UserResponse", "Token", "TokenData",
    "UserPreferenceCreate", "UserPreferenceUpdate", "UserPreferenceResponse",
    
    # 从speech.py导出
    "SpeechRequest", "SpeechResponse", "VoiceRecordCreate", "VoiceRecordResponse",
    
    # 从trip.py导出（移除费用相关模型）
    "TripCreate", "TripUpdate", "TripResponse", "Activity", "ItineraryCreate", 
    "ItineraryResponse", "POIRecommendationResponse",
    
    # 从ai.py导出
    "AIPlanRequest", "AIPlanResponse", "AIRecommendationRequest", "AIRecommendationResponse",
    
    # 从expense.py导出
    "ExpenseCreate", "ExpenseUpdate", "ExpenseResponse", "ExpenseSummaryResponse"
]