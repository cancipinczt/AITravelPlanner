from fastapi import APIRouter, Depends, HTTPException, status
from app.core.supabase_client import get_supabase_client
from app.core.auth import get_current_user
from app.schemas.auth import UserResponse
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