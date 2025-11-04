from fastapi import APIRouter

router = APIRouter()

@router.get("/health")
async def health_check():
    return {"status": "healthy", "message": "API服务运行正常"}

@router.get("/info")
async def api_info():
    return {
        "name": "AI旅行规划师API",
        "version": "1.0.0",
        "description": "基于AI的智能旅行规划服务"
    }