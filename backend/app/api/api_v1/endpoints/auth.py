from fastapi import APIRouter, Depends, HTTPException, status
from datetime import timedelta
from app.core.supabase_client import get_supabase_client
from app.core.auth import (
    create_access_token,
    get_current_user, ACCESS_TOKEN_EXPIRE_MINUTES,
    verify_password, get_password_hash
)
from app.schemas.auth import UserCreate, UserLogin, UserResponse, Token
from supabase import Client

router = APIRouter()

@router.post("/register", response_model=Token)
async def register(user_data: UserCreate, supabase: Client = Depends(get_supabase_client)):
    try:
        # 检查用户名是否已存在
        existing_user = supabase.table("users").select("*").eq("username", user_data.username).execute()
        if existing_user.data:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already taken"
            )
        
        # 创建新用户（直接插入users表）
        hashed_password = get_password_hash(user_data.password)
        new_user = {
            "username": user_data.username,
            "password_hash": hashed_password,
            "is_active": True
        }
        
        result = supabase.table("users").insert(new_user).execute()
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to create user"
            )
        
        # 创建访问令牌
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        
        # 构建UserResponse
        user_response = UserResponse(
            id=result.data[0]["id"],
            username=result.data[0]["username"],
            created_at=result.data[0].get("created_at"),
            is_active=result.data[0].get("is_active", True)
        )
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except Exception as e:
        error_msg = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {error_msg}"
        )

import time

@router.post("/login", response_model=Token)
async def login(user_data: UserLogin, supabase: Client = Depends(get_supabase_client)):
    start_time = time.time()
    try:
        # 记录数据库查询时间
        db_start = time.time()
        result = supabase.table("users").select("id,username,password_hash,created_at,is_active").eq("username", user_data.username).execute()
        db_time = time.time() - db_start
        
        if not result.data:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        
        db_user = result.data[0]
        
        # 密码验证时间
        pwd_start = time.time()
        if not verify_password(user_data.password, db_user["password_hash"]):
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect username or password"
            )
        pwd_time = time.time() - pwd_start
        
        # JWT创建时间
        jwt_start = time.time()
        access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": user_data.username}, expires_delta=access_token_expires
        )
        jwt_time = time.time() - jwt_start
        
        user_response = UserResponse(
            id=db_user["id"],
            username=db_user["username"],
            created_at=db_user.get("created_at"),
            is_active=db_user.get("is_active", True)
        )
        
        total_time = time.time() - start_time
        print(f"登录性能: 总时间={total_time:.3f}s, 数据库={db_time:.3f}s, 密码验证={pwd_time:.3f}s, JWT={jwt_time:.3f}s")
        
        return {
            "access_token": access_token,
            "token_type": "bearer",
            "user": user_response
        }
    except Exception as e:
        total_time = time.time() - start_time
        print(f"登录失败，耗时: {total_time:.3f}s")
        error_msg = str(e)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Login failed: {error_msg}"
        )

@router.get("/me", response_model=UserResponse)
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return UserResponse(**current_user)