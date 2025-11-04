from fastapi import APIRouter, HTTPException
from typing import List

router = APIRouter()

# 临时数据 - 实际项目中应该从数据库获取
sample_travel_plans = [
    {
        "id": 1,
        "destination": "北京",
        "duration": "3天2晚",
        "budget": 2000,
        "season": "春季"
    },
    {
        "id": 2, 
        "destination": "上海",
        "duration": "4天3晚", 
        "budget": 3000,
        "season": "秋季"
    }
]

@router.get("/travel-plans")
async def get_travel_plans():
    return {"travel_plans": sample_travel_plans}

@router.get("/travel-plans/{plan_id}")
async def get_travel_plan(plan_id: int):
    plan = next((p for p in sample_travel_plans if p["id"] == plan_id), None)
    if not plan:
        raise HTTPException(status_code=404, detail="旅行计划未找到")
    return {"travel_plan": plan}

@router.post("/travel-plans")
async def create_travel_plan():
    return {"message": "创建旅行计划功能待实现"}