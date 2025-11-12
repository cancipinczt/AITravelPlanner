#!/bin/sh

# 设置默认环境变量（如果未设置）
export VITE_API_BASE_URL=${VITE_API_BASE_URL:-"http://backend:8000/api/v1"}
export VITE_MAP_API_KEY=${VITE_MAP_API_KEY:-"9295de95eb57c1a6e73d0e9a10058771"}
export VITE_MAP_SECURITY_CODE=${VITE_MAP_SECURITY_CODE:-"8ec3794ae8a2dfdd6d4c4ef3fc4d8189"}

# 创建环境变量配置文件
cat > /usr/share/nginx/html/env-config.js << EOF
window.env = {
  VITE_API_BASE_URL: "${VITE_API_BASE_URL}",
  VITE_MAP_API_KEY: "${VITE_MAP_API_KEY}",
  VITE_MAP_SECURITY_CODE: "${VITE_MAP_SECURITY_CODE}"
};
EOF

# 启动nginx
exec nginx -g 'daemon off;'
