#!/bin/bash

# ==========================================
# Formy Backend 启动脚本
# ==========================================

set -e

echo "🚀 Starting Formy Backend..."

# 检查环境变量
if [ -z "$REDIS_HOST" ]; then
    echo "⚠️  REDIS_HOST not set, using default: localhost"
    export REDIS_HOST=localhost
fi

if [ -z "$REDIS_PORT" ]; then
    echo "⚠️  REDIS_PORT not set, using default: 6379"
    export REDIS_PORT=6379
fi

# 创建必要的目录
echo "📁 Creating directories..."
mkdir -p uploads/source uploads/reference uploads/result

# 检查运行模式
MODE=${MODE:-production}

if [ "$MODE" = "development" ]; then
    echo "🔧 Starting in DEVELOPMENT mode..."
    uvicorn app.main:app \
        --host 0.0.0.0 \
        --port 8000 \
        --reload \
        --log-level debug
else
    echo "🏭 Starting in PRODUCTION mode..."
    
    # 获取 CPU 核心数
    WORKERS=${WORKERS:-2}
    
    # 使用 gunicorn + uvicorn workers
    gunicorn app.main:app \
        --workers $WORKERS \
        --worker-class uvicorn.workers.UvicornWorker \
        --bind 0.0.0.0:8000 \
        --timeout 120 \
        --access-logfile - \
        --error-logfile - \
        --log-level info
fi

