from .health import router as health_router
from .travel import router as travel_router
from .auth import router as auth_router
from .user import router as user_router
from .trips import router as trips_router
from .ai import router as ai_router
from .speech import router as speech_router

__all__ = [
    "health_router",
    "travel_router", 
    "auth_router",
    "user_router",
    "trips_router",
    "ai_router",
    "speech_router"
]