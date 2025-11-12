# 构建阶段
FROM node:18-alpine as build-stage

WORKDIR /app

# 复制package文件
COPY package*.json ./

# 安装依赖
RUN npm ci

# 复制源代码
COPY . .

# 构建应用（使用生产环境变量）
RUN npm run build

# 生产阶段
FROM nginx:alpine as production-stage

# 安装gettext包用于envsubst命令
RUN apk add --no-cache gettext

# 复制构建结果到nginx
COPY --from=build-stage /app/dist /usr/share/nginx/html

# 创建一个脚本用于运行时替换环境变量
COPY docker-entrypoint.sh /docker-entrypoint.sh
RUN chmod +x /docker-entrypoint.sh

# 复制nginx配置
COPY nginx.conf /etc/nginx/nginx.conf

# 暴露端口
EXPOSE 80

# 健康检查
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:80 || exit 1

# 使用自定义入口点脚本
ENTRYPOINT ["/docker-entrypoint.sh"]

# 启动nginx
CMD ["nginx", "-g", "daemon off;"]