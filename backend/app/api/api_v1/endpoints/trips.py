from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from app.core.supabase_client import get_supabase_client
from app.core.auth import get_current_user
from app.schemas.trip import TripCreate, TripResponse, TripUpdate, ExpenseCreate, ExpenseResponse, TripBriefResponse
from decimal import Decimal

router = APIRouter()

# 辅助函数：处理Decimal和UUID类型的序列化
def serialize_fields(data_dict):
    """将字典中的Decimal和UUID字段转换为JSON可序列化的类型"""
    serialized = {}
    for key, value in data_dict.items():
        if isinstance(value, Decimal):
            # 将Decimal转换为float
            serialized[key] = float(value)
        elif isinstance(value, UUID):
            # 将UUID转换为字符串
            serialized[key] = str(value)
        else:
            serialized[key] = value
    return serialized

# 旅行计划API - 按照简化后的表结构

@router.post("/trips", response_model=TripResponse, status_code=status.HTTP_201_CREATED)
async def create_trip(
    trip_data: TripCreate,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """创建旅行计划"""
    # 创建旅行计划 - 使用Supabase插入数据
    trip_dict = trip_data.dict()
    trip_dict['user_id'] = str(current_user['id'])
    
    # 序列化字段（处理Decimal和UUID）
    trip_dict = serialize_fields(trip_dict)
    
    response = supabase.table('trips').insert(trip_dict).execute()
    
    if response.data:
        return response.data[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="创建旅行计划失败"
        )

@router.get("/trips", response_model=List[TripBriefResponse])
async def get_trips(
    skip: int = 0,
    limit: int = 100,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取用户的所有旅行计划（简要信息）"""
    # 获取旅行计划数据，同时关联用户偏好表获取偏好名称
    response = supabase.table('trips').select(
        'id, title, destination, budget, travelers_count, days, preference_id, created_at'
    ).eq('user_id', str(current_user['id'])).range(skip, skip + limit - 1).execute()
    
    if not response.data:
        return []
    
    # 处理每个旅行计划，获取偏好名称
    trips_with_preference_names = []
    for trip in response.data:
        trip_with_preference = dict(trip)
        
        # 如果有preference_id，获取偏好名称
        if trip.get('preference_id'):
            pref_response = supabase.table('user_preferences').select('name').eq('id', str(trip['preference_id'])).execute()
            if pref_response.data:
                trip_with_preference['preference_name'] = pref_response.data[0]['name']
            else:
                trip_with_preference['preference_name'] = None
        else:
            trip_with_preference['preference_name'] = None
        
        trips_with_preference_names.append(trip_with_preference)
    
    return trips_with_preference_names

@router.get("/trips/{trip_id}", response_model=TripResponse)
async def get_trip(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取特定旅行计划详情"""
    response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
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
    check_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not check_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 更新字段
    update_data = trip_data.dict(exclude_unset=True)
    
    # 序列化字段（处理Decimal和UUID）
    update_data = serialize_fields(update_data)
    
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
    check_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
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

# 费用管理API - 保持不变
@router.post("/trips/{trip_id}/expenses", response_model=ExpenseResponse, status_code=status.HTTP_201_CREATED)
async def create_expense(
    trip_id: UUID,
    expense_data: ExpenseCreate,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """添加费用记录"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 创建费用记录
    expense_dict = expense_data.dict()
    expense_dict['trip_id'] = str(trip_id)
    
    # 序列化字段（处理Decimal和UUID）
    expense_dict = serialize_fields(expense_dict)
    
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
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
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
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # TODO: 实现预算分析逻辑
    return {"message": "预算分析功能待实现"}