# AI旅行规划师 - 智能行程规划功能API文档

## 概述

本文档描述了智能行程规划功能的API接口，按照需求文档2.0.md的规范实现。

## 基础信息

- **基础URL**: `http://localhost:8000/api/v1`
- **认证**: 需要JWT令牌（Bearer Token）

## API端点

### 旅行计划API (4.1.3)

#### 创建旅行计划
- **端点**: `POST /trips`
- **描述**: 创建新的旅行计划
- **请求体**: 
```json
{
  "destination": "北京",
  "start_date": "2024-06-01",
  "end_date": "2024-06-04",
  "budget": 3000,
  "preferences": {
    "interests": ["历史", "文化"],
    "food_preferences": ["中餐"]
  }
}
```

#### 获取旅行计划列表
- **端点**: `GET /trips`
- **描述**: 获取用户的旅行计划列表

#### 获取旅行计划详情
- **端点**: `GET /trips/{trip_id}`
- **描述**: 获取特定旅行计划的详细信息

#### 更新旅行计划
- **端点**: `PUT /trips/{trip_id}`
- **描述**: 更新旅行计划信息

#### 删除旅行计划
- **端点**: `DELETE /trips/{trip_id}`
- **描述**: 删除旅行计划

### AI规划API (4.1.6)

#### AI生成旅行计划
- **端点**: `POST /ai/plan`
- **描述**: 使用AI生成个性化旅行计划
- **请求体**:
```json
{
  "destination": "北京",
  "duration_days": 5,
  "budget": 3000,
  "preferences": {
    "interests": ["历史", "文化"],
    "travel_style": "休闲"
  }
}
```

#### 获取景点推荐
- **端点**: `POST /ai/recommend`
- **描述**: 获取目的地景点推荐

#### 优化行程
- **端点**: `POST /ai/optimize`
- **描述**: 优化现有行程安排

#### 语音输入处理
- **端点**: `POST /ai/speech`
- **描述**: 处理语音输入生成旅行需求

## 数据库表结构

### 旅行计划表 (trips) - 5.1.3
- `id`: UUID主键
- `user_id`: 用户ID（外键）
- `destination`: 目的地
- `start_date`: 开始日期
- `end_date`: 结束日期
- `duration_days`: 行程天数
- `budget`: 预算
- `preferences`: 偏好设置（JSON）
- `status`: 状态（draft/planning/completed/cancelled）

### 行程详情表 (trip_itineraries) - 5.1.4
- `id`: UUID主键
- `trip_id`: 旅行计划ID（外键）
- `day_number`: 天数
- `date`: 日期
- `activities`: 活动安排（JSON）
- `accommodation`: 住宿信息
- `transportation`: 交通信息

### 景点推荐表 (poi_recommendations) - 5.1.6
- `id`: UUID主键
- `trip_id`: 旅行计划ID（外键）
- `name`: 景点名称
- `type`: 景点类型
- `location`: 位置信息
- `latitude/longitude`: 经纬度坐标
- `description`: 描述
- `rating`: 评分

## 外部API集成

### AI服务
- **阿里云AI**: 用于行程规划和推荐
- **OpenAI**: 备用AI服务

### 地图服务
- **高德地图/百度地图**: 用于地理位置和路线规划
- **Google Maps**: 国际目的地支持

### 图片服务
- **Unsplash/Pexels**: 提供高质量旅行图片

### 语音服务
- **阿里云语音识别**: 支持语音输入功能

## 部署说明

1. 配置环境变量（.env文件）
2. 执行数据库迁移脚本
3. 安装依赖：`pip install -r requirements.txt`
4. 启动服务：`uvicorn main:app --reload`

## 测试

使用初始化脚本测试功能：
```bash
python init_database.py
```

## 前端集成建议

- 使用地图为主的交互界面
- 清晰的行程展示时间线
- 集成美观的景点图片
- 支持语音输入功能
- 响应式设计支持移动端