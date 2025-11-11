from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.core.supabase_client import get_supabase_client
from app.core.auth import get_current_user
from app.schemas.trip import (
    TripCreate, TripResponse, TripUpdate, 
    ItineraryCreate, ItineraryResponse,
    ExpenseCreate, ExpenseResponse,
    POIRecommendationResponse
)
# 更新导入：使用新的AI模型定义
from app.schemas.ai import AIPlanRequest, AIPlanResponse

router = APIRouter()

# 旅行计划API - 按照需求文档4.1.3规范

@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_data: TripCreate,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """创建旅行计划"""
    # 验证日期逻辑
    if trip_data.start_date >= trip_data.end_date:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="结束日期必须晚于开始日期"
        )
    
    # 创建旅行计划 - 使用Supabase插入数据
    trip_dict = trip_data.dict()
    trip_dict['user_id'] = str(current_user.id)
    
    response = supabase.table('trips').insert(trip_dict).execute()
    
    if response.data:
        return response.data[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建旅行计划失败"
        )

@router.get("/trips", response_model=List[TripResponse])
async def get_trips(
    skip: int = 0,
    limit: int = 100,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取用户的所有旅行计划"""
    response = supabase.table('trips').select('*').eq('user_id', str(current_user.id)).range(skip, skip + limit - 1).execute()
    
    return response.data if response.data else []

@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取特定旅行计划详情"""
    response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    return response.data[0]

@router.put("/trips/{trip_id}", response_model=TripResponse)
async def update_trip(
    trip_id: UUID,
    trip_data: TripUpdate,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """更新旅行计划"""
    # 先验证旅行计划存在且属于当前用户
    check_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not check_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 更新字段
    update_data = trip_data.dict(exclude_unset=True)
    response = supabase.table('trips').update(update_data).eq('id', str(trip_id)).execute()
    
    if response.data:
        return response.data[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新旅行计划失败"
        )

@router.delete("/trips/{trip_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_trip(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """删除旅行计划"""
    # 先验证旅行计划存在且属于当前用户
    check_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not check_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 删除旅行计划
    response = supabase.table('trips').delete().eq('id', str(trip_id)).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除旅行计划失败"
        )
    
    return None

@router.post("/trips/{trip_id}/generate", response_model=AIPlanResponse)
async def generate_itinerary(
    trip_id: UUID,
    ai_request: AIPlanRequest,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """AI生成行程 - 基于现有旅行计划生成AI行程"""
    # 验证旅行计划存在且属于当前用户
    response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # TODO: 集成阿里云百炼AI服务
    # 这里先返回模拟数据
    return AIPlanResponse(
        itinerary="基于现有旅行计划的AI生成行程（待实现）",
        budget_usage={},
        recommendations=[],
        weather_info={},
        status="success"
    )

@router.get("/trips/{trip_id}/itinerary", response_model=List[ItineraryResponse])
async def get_itinerary(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取行程详情"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 获取行程详情
    response = supabase.table('trip_itineraries').select('*').eq('trip_id', str(trip_id)).execute()
    
    return response.data if response.data else []

# 费用管理API - 按照需求文档4.1.4规范

@router.post("/trips/{trip_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    trip_id: UUID,
    expense_data: ExpenseCreate,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """添加费用记录"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 创建费用记录
    expense_dict = expense_data.dict()
    expense_dict['trip_id'] = str(trip_id)
    
    response = supabase.table('expenses').insert(expense_dict).execute()
    
    if response.data:
        return response.data[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建费用记录失败"
        )

@router.get("/trips/{trip_id}/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取费用列表"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    response = supabase.table('expenses').select('*').eq('trip_id', str(trip_id)).execute()
    
    return response.data if response.data else []

@router.get("/trips/{trip_id}/budget-analysis")
async def get_budget_analysis(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """预算分析报告"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user.id)).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # TODO: 实现预算分析逻辑
    return {"message": "预算分析功能待实现"}