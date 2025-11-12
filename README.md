# AI旅行规划师 (AI Travel Planner)

AI4SE homework3
基于AI的智能旅行规划Web应用，提供个性化的旅行路线规划、费用管理和地图导航等功能。

## 项目地址
**GitHub仓库**: https://github.com/cancipinczt/AITravelPlanner

## 核心功能

1. **智能行程规划**: 支持语音/文字输入，AI自动生成个性化旅行路线
2. **费用预算管理**: AI预算分析，语音记录旅行开销
3. **地图导航**: 基于高德地图，可以搜索地点，导航路线
4. **用户管理**: 注册登录系统，云端数据同步

## 技术栈

### 前端
- Vue.js 3 + TypeScript + Element Plus
- 高德地图API + 科大讯飞语音识别API

### 后端
- Python + FastAPI + Supabase
- 阿里云百炼平台AI服务

### 部署
- Docker + GitHub Actions + 阿里云容器镜像服务

## 快速部署

### 使用Docker Compose部署

```bash
# 下载docker-compose.prod.yml文件
wget https://raw.githubusercontent.com/cancipinczt/AITravelPlanner/main/docker-compose.prod.yml

# 启动服务
docker-compose -f docker-compose.prod.yml up -d
```

## API Key配置

**重要**: 所有必要的API密钥已在docker-compose.prod.yml中预配置，无需额外设置。

**已配置的密钥包括**：
- 阿里云百炼平台AI服务密钥
- 高德地图API密钥  
- 科大讯飞语音识别API密钥
- Supabase数据库配置
- 应用安全密钥

**部署时直接使用**：
```bash
docker-compose -f docker-compose.prod.yml up -d
```

应用将自动使用预配置的密钥正常运行。

## 访问地址
- 前端应用: http://localhost:80 或 http://localhost
- 后端API文档: http://localhost:8000/docs

## 项目结构
```
AITravelPlanner/ 
├── frontend/ # Vue.js前端 
├── backend/ # FastAPI后端
├── .github/workflows/ # CI/CD配置 
└── docker-compose.prod.yml # 生产环境配置
```

## 许可证
MIT License