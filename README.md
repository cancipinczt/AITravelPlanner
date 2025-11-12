# AI旅行规划师 (AI Travel Planner)

AI4SE homework3
基于AI的智能旅行规划Web应用，提供个性化的旅行路线规划、费用管理和实时辅助功能。

## 技术栈

### 前端

- **框架**: Vue.js 3 + TypeScript
- **UI组件**: Element Plus
- **构建工具**: Vite
- **地图服务**: 高德地图API
- **语音识别**: 科大讯飞API
- **状态管理**: Pinia
- **路由**: Vue Router

### 后端

- **框架**: Python + FastAPI
- **数据库**: PostgreSQL + Supabase
- **认证**: Supabase Auth
- **AI服务**: 阿里云百炼平台
- **文件存储**: 阿里云OSS

### 部署

- **容器化**: Docker + Docker Compose
- **CI/CD**: GitHub Actions
- **镜像仓库**: 阿里云容器镜像服务

## 项目结构

AITravelPlanner/
├── frontend/ # 前端项目
├── backend/ # 后端项目
├── docker-compose.yml # 开发环境
├── .github/ # CI/CD配置
└── docs/ # 项目文档

## 快速开始

### 开发环境

```bash
# 克隆项目
git clone <repository-url>
cd AITravelPlanner

# 启动开发环境
docker-compose up -d
```

### 生产部署

```bash
# 构建生产镜像
docker-compose -f docker-compose.prod.yml up -d
```

## API文档

访问 `http://localhost:8000/docs` 查看后端API文档。

## 许可证

MIT License
