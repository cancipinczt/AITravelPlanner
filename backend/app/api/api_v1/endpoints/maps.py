from fastapi import APIRouter, HTTPException, Query
from typing import Optional, Dict, Any
from app.core.map_client import map_client

router = APIRouter()

@router.get("/geocode")
async def geocode_address(
    address: str = Query(..., description="要解析的地址"),
    city: str = Query(None, description="城市限定（可选）")
) -> Dict[str, Any]:
    """
    地址解析接口 - 地理编码
    - 将地址文字转换为地理坐标
    - 支持城市限定搜索
    """
    try:
        result = await map_client.geocode(address, city)
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "地址解析失败"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/reverse-geocode")
async def reverse_geocode(
    location: str = Query(..., description="经纬度坐标，格式：经度,纬度")
) -> Dict[str, Any]:
    """
    逆地理编码接口
    - 将地理坐标转换为地址文字
    - 返回详细地址信息和周边POI
    """
    try:
        result = await map_client.reverse_geocode(location)
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "逆地理编码失败"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/route")
async def route_planning(
    origin: str = Query(..., description="起点坐标，格式：经度,纬度"),
    destination: str = Query(..., description="终点坐标，格式：经度,纬度"),
    strategy: int = Query(0, description="路径策略：0-速度优先,1-费用优先,2-距离优先,3-不走高速")
) -> Dict[str, Any]:
    """
    路线规划接口
    - 计算两点之间的最优路线
    - 支持多种出行策略
    - 返回距离、时间、详细路径等信息
    """
    try:
        result = await map_client.route_planning(origin, destination, strategy)
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "路线规划失败"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/poi")
async def search_poi(
    keywords: str = Query(..., description="搜索关键词"),
    city: str = Query(None, description="城市限定（可选）"),
    types: str = Query(None, description="POI类型限定（可选）"),
    location: str = Query(None, description="中心点坐标，格式：经度,纬度"),
    radius: int = Query(3000, description="搜索半径（米），默认3000米")
) -> Dict[str, Any]:
    """
    兴趣点搜索接口
    - 搜索特定区域内的景点、餐厅、酒店等
    - 支持关键词搜索、周边搜索、分类搜索
    - 返回POI列表及详细信息
    """
    try:
        result = await map_client.search_poi(keywords, city, types, location, radius)
        if result.get("status") == "success":
            return {
                "success": True,
                "data": result
            }
        else:
            raise HTTPException(status_code=400, detail=result.get("message", "POI搜索失败"))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")

@router.get("/static-map")
async def get_static_map(
    location: str = Query(..., description="中心点坐标，格式：经度,纬度"),
    zoom: int = Query(15, description="缩放级别，1-18，默认15"),
    size: str = Query("400*300", description="图片尺寸，格式：宽*高"),
    markers: str = Query(None, description="标记点，格式：经度,纬度,标记样式"),
    labels: str = Query(None, description="标签，格式：经度,纬度,标签内容")
) -> Dict[str, Any]:
    """
    静态地图接口
    - 生成地图图片
    - 支持标记点和标签
    - 注意：返回的是图片URL，适合生成地图快照
    """
    try:
        result = await map_client.static_map(location, zoom, size, markers, labels)
        return {
            "success": True,
            "data": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"服务器错误: {str(e)}")