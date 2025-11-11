from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from uuid import UUID
from decimal import Decimal
from datetime import date

from app.core.supabase_client import get_supabase_client
from app.core.auth import get_current_user
from app.schemas.expense import ExpenseCreate, ExpenseUpdate, ExpenseResponse, ExpenseSummaryResponse

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
        elif isinstance(value, date):
            # 将date转换为字符串
            serialized[key] = value.isoformat()
        else:
            serialized[key] = value
    return serialized

# 辅助函数：解析日期字符串
def parse_date(date_str: str) -> date:
    """将日期字符串解析为date对象"""
    try:
        return date.fromisoformat(date_str)
    except (ValueError, TypeError):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="日期格式无效，请使用YYYY-MM-DD格式"
        )

# 1. 添加费用记录
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

# 2. 获取费用列表
@router.get("/trips/{trip_id}/expenses", response_model=List[ExpenseResponse])
async def get_expenses(
    trip_id: UUID,
    skip: int = 0,
    limit: int = 100,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
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
    
    # 构建查询
    query = supabase.table('expenses').select('*').eq('trip_id', str(trip_id))
    
    # 添加日期范围过滤
    if start_date:
        query = query.gte('expense_date', start_date.isoformat())
    if end_date:
        query = query.lte('expense_date', end_date.isoformat())
    
    # 添加分页和排序
    response = query.order('expense_date', desc=True).range(skip, skip + limit - 1).execute()
    
    return response.data if response.data else []

# 3. 获取费用详情
@router.get("/trips/{trip_id}/expenses/{expense_id}", response_model=ExpenseResponse)
async def get_expense(
    trip_id: UUID,
    expense_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取费用详情"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 获取费用记录
    response = supabase.table('expenses').select('*').eq('id', str(expense_id)).eq('trip_id', str(trip_id)).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="费用记录不存在"
        )
    
    return response.data[0]

# 4. 更新费用记录
@router.put("/trips/{trip_id}/expenses/{expense_id}", response_model=ExpenseResponse)
async def update_expense(
    trip_id: UUID,
    expense_id: UUID,
    expense_data: ExpenseUpdate,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """更新费用记录"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 验证费用记录存在
    expense_response = supabase.table('expenses').select('*').eq('id', str(expense_id)).eq('trip_id', str(trip_id)).execute()
    
    if not expense_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="费用记录不存在"
        )
    
    # 更新字段
    update_data = expense_data.dict(exclude_unset=True)
    
    # 序列化字段（处理Decimal和UUID）
    update_data = serialize_fields(update_data)
    
    response = supabase.table('expenses').update(update_data).eq('id', str(expense_id)).execute()
    
    if response.data:
        return response.data[0]
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="更新费用记录失败"
        )

# 5. 删除费用记录
@router.delete("/trips/{trip_id}/expenses/{expense_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_expense(
    trip_id: UUID,
    expense_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """删除费用记录"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 验证费用记录存在
    expense_response = supabase.table('expenses').select('*').eq('id', str(expense_id)).eq('trip_id', str(trip_id)).execute()
    
    if not expense_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="费用记录不存在"
        )
    
    # 删除费用记录
    response = supabase.table('expenses').delete().eq('id', str(expense_id)).execute()
    
    if not response.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="删除费用记录失败"
        )
    
    return None

# 6. 获取特定旅行计划的总费用统计
@router.get("/trips/{trip_id}/expenses/summary", response_model=ExpenseSummaryResponse)
async def get_trip_expense_summary(
    trip_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取特定旅行计划的总费用统计"""
    # 验证旅行计划权限
    trip_response = supabase.table('trips').select('*').eq('id', str(trip_id)).eq('user_id', str(current_user['id'])).execute()
    
    if not trip_response.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="旅行计划不存在"
        )
    
    # 获取该旅行计划的所有费用记录
    expenses_response = supabase.table('expenses').select('amount').eq('trip_id', str(trip_id)).execute()
    
    # 计算总金额和记录数量
    total_amount = 0.0
    expense_count = 0
    
    if expenses_response.data:
        expense_count = len(expenses_response.data)
        # 安全地计算总金额，处理可能的None值
        for expense in expenses_response.data:
            if expense.get('amount') is not None:
                try:
                    total_amount += float(expense['amount'])
                except (ValueError, TypeError):
                    # 如果金额转换失败，跳过该记录
                    continue
    
    return ExpenseSummaryResponse(
        total_amount=round(total_amount, 2),  # 保留2位小数
        expense_count=expense_count
    )

# 7. 获取用户所有旅行计划的总费用统计
@router.get("/users/{user_id}/expenses/summary", response_model=ExpenseSummaryResponse)
async def get_user_expense_summary(
    user_id: UUID,
    supabase = Depends(get_supabase_client),
    current_user = Depends(get_current_user)
):
    """获取用户所有旅行计划的总费用统计"""
    # 验证用户权限（只能查看自己的数据）
    if str(current_user['id']) != str(user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问其他用户的数据"
        )
    
    # 获取用户的所有旅行计划
    trips_response = supabase.table('trips').select('id').eq('user_id', str(user_id)).execute()
    
    if not trips_response.data:
        # 如果用户没有旅行计划，返回默认值
        return ExpenseSummaryResponse(total_amount=0.0, expense_count=0)
    
    # 获取所有旅行计划的费用记录
    trip_ids = [str(trip['id']) for trip in trips_response.data]
    
    # 由于Supabase的IN查询限制，我们分批查询
    total_amount = 0.0
    expense_count = 0
    
    # 每次处理最多10个trip_id
    batch_size = 10
    for i in range(0, len(trip_ids), batch_size):
        batch_trip_ids = trip_ids[i:i + batch_size]
        
        # 构建IN查询
        expenses_response = supabase.table('expenses').select('amount').in_('trip_id', batch_trip_ids).execute()
        
        if expenses_response.data:
            expense_count += len(expenses_response.data)
            # 安全地计算总金额，处理可能的None值
            for expense in expenses_response.data:
                if expense.get('amount') is not None:
                    try:
                        total_amount += float(expense['amount'])
                    except (ValueError, TypeError):
                        # 如果金额转换失败，跳过该记录
                        continue
    
    return ExpenseSummaryResponse(
        total_amount=round(total_amount, 2),  # 保留2位小数
        expense_count=expense_count
    )