import httpx
import json
from typing import Dict, Any, Optional, List, Union
from app.core.config import settings

class MapClient:
    """高德地图服务客户端"""
    
    def __init__(self):
        self.api_key = settings.MAP_API_KEY
        self.base_url = "https://restapi.amap.com/v3"
    
    async def _make_request(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """发送HTTP请求到高德地图API"""
        try:
            params["key"] = self.api_key
            params["output"] = "json"
            
            async with httpx.AsyncClient() as client:
                response = await client.get(f"{self.base_url}/{endpoint}", params=params)
                response.raise_for_status()
                
                # 对于静态地图，直接返回URL而不是解析JSON
                if endpoint == "staticmap":
                    return {
                        "status": "success",
                        "image_url": str(response.url)
                    }
                
                return response.json()
        except Exception as e:
            print(f"高德地图API请求错误: {str(e)}")
            return {"status": "0", "info": str(e)}
    
    async def geocode(self, address: str, city: str = None) -> Dict[str, Any]:
        """地理编码 - 地址转坐标"""
        params = {"address": address}
        if city:
            params["city"] = city
        
        result = await self._make_request("geocode/geo", params)
        return self._parse_geocode_result(result)
    
    async def reverse_geocode(self, location: str) -> Dict[str, Any]:
        """逆地理编码 - 坐标转地址"""
        params = {"location": location}
        result = await self._make_request("geocode/regeo", params)
        return self._parse_reverse_geocode_result(result)
    
    async def route_planning(self, origin: str, destination: str, strategy: int = 0) -> Dict[str, Any]:
        """路径规划 - 支持多种出行方式"""
        try:
            # 首先将地址转换为坐标
            origin_coords = await self._address_to_coords(origin)
            destination_coords = await self._address_to_coords(destination)
            
            if not origin_coords or not destination_coords:
                return {"status": "error", "message": "地址解析失败"}
            
            params = {
                "origin": origin_coords,
                "destination": destination_coords,
                "strategy": strategy  # 0:速度优先, 1:费用优先, 2:距离优先, 3:不走高速
            }
            result = await self._make_request("direction/driving", params)
            return self._parse_route_result(result)
        except Exception as e:
            print(f"路径规划错误: {str(e)}")
            return {"status": "error", "message": f"路径规划失败: {str(e)}"}
    
    async def _address_to_coords(self, address: str) -> str:
        """将地址转换为经纬度坐标"""
        try:
            params = {"address": address}
            result = await self._make_request("geocode/geo", params)
            
            if result.get("status") == "1" and result.get("geocodes"):
                geocode = result["geocodes"][0]
                return geocode.get("location")  # 返回格式：经度,纬度
            return None
        except Exception as e:
            print(f"地址转坐标错误: {str(e)}")
            return None
    
    async def search_poi(self, keywords: str, city: str = None, types: str = None, 
                        location: str = None, radius: int = 3000) -> Dict[str, Any]:
        """POI搜索 - 支持多种搜索方式"""
        params = {"keywords": keywords}
        if city:
            params["city"] = city
        if types:
            params["types"] = types
        if location:
            params["location"] = location
            params["radius"] = radius
        
        result = await self._make_request("place/text", params)
        return self._parse_poi_result(result)
    
    async def static_map(self, location: str, zoom: int = 15, size: str = "400*300", 
                        markers: str = None, labels: str = None) -> Dict[str, Any]:
        """静态地图 - 生成地图图片"""
        try:
            params = {
                "location": location,
                "zoom": zoom,
                "size": size
            }
            if markers:
                params["markers"] = markers
            if labels:
                params["labels"] = labels
            
            result = await self._make_request("staticmap", params)
            return result
        except Exception as e:
            print(f"静态地图错误: {str(e)}")
            return {"status": "error", "message": f"静态地图生成失败: {str(e)}"}
    
    def _parse_geocode_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """解析地理编码结果"""
        if result.get("status") == "1" and result.get("geocodes"):
            geocode = result["geocodes"][0]
            return {
                "status": "success",
                "location": geocode.get("location"),
                "formatted_address": geocode.get("formatted_address"),
                "province": geocode.get("province"),
                "city": geocode.get("city"),
                "district": geocode.get("district")
            }
        return {"status": "error", "message": result.get("info", "地理编码失败")}
    
    def _parse_reverse_geocode_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """解析逆地理编码结果"""
        if result.get("status") == "1" and result.get("regeocode"):
            regeocode = result["regeocode"]
            return {
                "status": "success",
                "formatted_address": regeocode.get("formatted_address"),
                "address_component": regeocode.get("addressComponent", {}),
                "pois": regeocode.get("pois", [])
            }
        return {"status": "error", "message": result.get("info", "逆地理编码失败")}
    
    def _parse_route_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """解析路径规划结果"""
        if result.get("status") == "1" and result.get("route"):
            route = result["route"]
            paths = route.get("paths", [])
            if paths:
                path = paths[0]
                return {
                    "status": "success",
                    "distance": path.get("distance"),  # 米
                    "duration": path.get("duration"),  # 秒
                    "steps": path.get("steps", []),
                    "toll_distance": path.get("toll_distance"),
                    "toll_road": path.get("toll_road", "").split(";")
                }
        return {"status": "error", "message": result.get("info", "路径规划失败")}
    
    def _parse_poi_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """解析POI搜索结果"""
        if result.get("status") == "1" and result.get("pois"):
            pois = result["pois"]
            return {
                "status": "success",
                "count": len(pois),
                "pois": [{
                    "id": poi.get("id"),
                    "name": poi.get("name"),
                    "type": poi.get("type"),
                    "location": poi.get("location"),
                    "address": poi.get("address"),
                    "tel": poi.get("tel"),
                    "distance": poi.get("distance"),
                    "business_area": poi.get("business_area")
                } for poi in pois]
            }
        return {"status": "error", "message": result.get("info", "POI搜索失败")}

# 创建全局地图客户端实例
map_client = MapClient()