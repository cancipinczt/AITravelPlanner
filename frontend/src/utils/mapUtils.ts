/**
 * 地图工具函数
 */

// 坐标转换工具
export const convertCoordinates = {
  // GPS坐标转高德坐标
  wgs84ToGcj02: (lng: number, lat: number): [number, number] => {
    // 简化的坐标转换（实际应该使用高德提供的转换服务）
    return [lng + 0.006, lat + 0.006]
  },
  
  // 高德坐标转GPS坐标
  gcj02ToWgs84: (lng: number, lat: number): [number, number] => {
    return [lng - 0.006, lat - 0.006]
  }
}

// 距离计算工具
export const calculateDistance = (point1: [number, number], point2: [number, number]): number => {
  const [lng1, lat1] = point1
  const [lng2, lat2] = point2
  
  const R = 6371 // 地球半径（公里）
  const dLat = (lat2 - lat1) * Math.PI / 180
  const dLng = (lng2 - lng1) * Math.PI / 180
  const a = Math.sin(dLat/2) * Math.sin(dLat/2) +
            Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
            Math.sin(dLng/2) * Math.sin(dLng/2)
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a))
  return R * c
}

// 地图样式配置
export const mapStyles = {
  normal: 'amap://styles/normal',
  satellite: 'amap://styles/satellite',
  dark: 'amap://styles/dark',
  light: 'amap://styles/light',
  fresh: 'amap://styles/fresh'
}

// 标记图标配置
export const markerIcons = {
  red: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_r.png',
  blue: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_b.png',
  green: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_g.png',
  yellow: 'https://webapi.amap.com/theme/v1.3/markers/n/mark_y.png'
}

// 路径规划策略
export const routeStrategies = {
  LEAST_TIME: 0,      // 速度优先
  LEAST_FEE: 1,       // 费用优先
  LEAST_DISTANCE: 2,  // 距离优先
  REAL_TRAFFIC: 4     // 实时路况
}