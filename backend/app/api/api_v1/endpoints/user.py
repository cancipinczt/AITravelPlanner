from fastapi import APIRouter, Depends, HTTPException, status
from app.core.auth import get_current_user
from app.core.supabase_client import get_supabase_client
from app.schemas.auth import UserResponse, UserPreferenceCreate, UserPreferenceUpdate, UserPreferenceResponse, UserPreferenceListResponse
from supabase import Client

router = APIRouter()

@router.get("/profile", response_model=UserResponse)
def get_user_profile(current_user: dict = Depends(get_current_user)):
    # 确保返回的数据格式正确
    return UserResponse(
        id=current_user["id"],
        username=current_user["username"],
        created_at=current_user.get("created_at"),
        is_active=current_user.get("is_active", True)
    )

@router.put("/profile", response_model=UserResponse)
def update_user_profile(
    user_data: UserResponse,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    # 检查用户名是否被其他用户使用
    if user_data.username != current_user["username"]:
        existing_user = supabase.table("users").select("*").eq("username", user_data.username).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
    
    # 更新用户信息
    result = supabase.table("users").update({
        "username": user_data.username,
        "updated_at": "now()"  # 添加更新时间
    }).eq("id", current_user["id"]).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user profile"
        )
    
    # 返回更新后的用户信息
    return UserResponse(
        id=result.data[0]["id"],
        username=result.data[0]["username"],
        created_at=result.data[0].get("created_at"),
        is_active=result.data[0].get("is_active", True)
    )

# 用户偏好管理接口 - 修改为支持多个偏好
@router.get("/preferences", response_model=UserPreferenceListResponse)
def get_user_preferences(
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """获取用户所有偏好设置"""
    result = supabase.table("user_preferences").select("*").eq("user_id", current_user["id"]).order("created_at", desc=True).execute()
    
    if not result.data:
        # 如果用户没有偏好设置，返回空列表
        return UserPreferenceListResponse(preferences=[])
    
    # 转换所有偏好数据
    preferences = []
    for preference_data in result.data:
        preferences.append(UserPreferenceResponse(
            id=preference_data["id"],
            user_id=preference_data["user_id"],
            name=preference_data.get("name", "未命名偏好"),
            travel_preferences=preference_data.get("travel_preferences"),
            special_requirements=preference_data.get("special_requirements"),
            created_at=preference_data.get("created_at"),
            updated_at=preference_data.get("updated_at")
        ))
    
    return UserPreferenceListResponse(preferences=preferences)

@router.post("/preferences", response_model=UserPreferenceResponse)
def create_user_preferences(
    preference_data: UserPreferenceCreate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """创建用户偏好设置 - 移除创建限制，支持多个偏好"""
    # 创建新的偏好设置
    result = supabase.table("user_preferences").insert({
        "user_id": current_user["id"],
        "name": preference_data.name,  # 新增：偏好名称
        "travel_preferences": preference_data.travel_preferences,
        "special_requirements": preference_data.special_requirements,
        "created_at": "now()",
        "updated_at": "now()"
    }).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to create user preferences"
        )
    
    created_preference = result.data[0]
    return UserPreferenceResponse(
        id=created_preference["id"],
        user_id=created_preference["user_id"],
        name=created_preference.get("name", "未命名偏好"),
        travel_preferences=created_preference.get("travel_preferences"),
        special_requirements=created_preference.get("special_requirements"),
        created_at=created_preference.get("created_at"),
        updated_at=created_preference.get("updated_at")
    )

@router.put("/preferences/{preference_id}", response_model=UserPreferenceResponse)
def update_user_preferences(
    preference_id: str,  # 确保这里接收的是字符串类型的preference_id
    preference_data: UserPreferenceUpdate,
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """更新特定偏好设置"""
    # 检查preference_id是否有效
    if not preference_id or preference_id == "undefined":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid preference ID"
        )
    
    # 检查偏好设置是否存在且属于当前用户
    existing_preference = supabase.table("user_preferences").select("*").eq("id", preference_id).eq("user_id", current_user["id"]).execute()
    
    if not existing_preference.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    # 更新偏好设置
    update_data = {}
    if preference_data.name is not None:
        update_data["name"] = preference_data.name
    if preference_data.travel_preferences is not None:
        update_data["travel_preferences"] = preference_data.travel_preferences
    if preference_data.special_requirements is not None:
        update_data["special_requirements"] = preference_data.special_requirements
    
    update_data["updated_at"] = "now()"
    
    result = supabase.table("user_preferences").update(update_data).eq("id", preference_id).execute()
    
    if not result.data:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update user preferences"
        )
    
    updated_preference = result.data[0]
    return UserPreferenceResponse(
        id=updated_preference["id"],
        user_id=updated_preference["user_id"],
        name=updated_preference.get("name", "未命名偏好"),
        travel_preferences=updated_preference.get("travel_preferences"),
        special_requirements=updated_preference.get("special_requirements"),
        created_at=updated_preference.get("created_at"),
        updated_at=updated_preference.get("updated_at")
    )

@router.delete("/preferences/{preference_id}")
def delete_user_preferences(
    preference_id: str,  # 确保这里接收的是字符串类型的preference_id
    current_user: dict = Depends(get_current_user),
    supabase: Client = Depends(get_supabase_client)
):
    """删除特定偏好设置"""
    # 检查preference_id是否有效
    if not preference_id or preference_id == "undefined":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid preference ID"
        )
    
    # 检查偏好设置是否存在且属于当前用户
    existing_preference = supabase.table("user_preferences").select("*").eq("id", preference_id).eq("user_id", current_user["id"]).execute()
    
    if not existing_preference.data:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Preference not found"
        )
    
    result = supabase.table("user_preferences").delete().eq("id", preference_id).execute()
    
    if result.data is None:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete user preferences"
        )
    
    return {"message": "User preference deleted successfully"}