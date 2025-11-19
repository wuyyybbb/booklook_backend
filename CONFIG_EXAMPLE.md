# 配置示例文档

## 环境变量配置

创建 `.env` 文件并添加以下配置：

```env
# 应用配置
APP_NAME=Formy
APP_VERSION=1.0.0
DEBUG=True

# API 配置
API_V1_PREFIX=/api/v1

# Redis 配置
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=

# 文件存储配置
UPLOAD_DIR=./uploads
RESULT_DIR=./results
MAX_UPLOAD_SIZE=10485760

# 任务配置
TASK_RETENTION_DAYS=7
MAX_CONCURRENT_TASKS_PER_USER=3

# JWT 配置（可选）
SECRET_KEY=formy-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Engine 配置文件路径
ENGINE_CONFIG_PATH=./engine_config.yml
```

## 配置说明

### Redis 配置
- `REDIS_HOST`: Redis 服务器地址（默认: localhost）
- `REDIS_PORT`: Redis 端口（默认: 6379）
- `REDIS_DB`: Redis 数据库编号（默认: 0）
- `REDIS_PASSWORD`: Redis 密码（可选，为空表示无密码）

### 文件存储配置
- `UPLOAD_DIR`: 上传文件存储目录
- `RESULT_DIR`: 结果文件存储目录
- `MAX_UPLOAD_SIZE`: 最大上传文件大小（字节，默认 10MB）

### 任务配置
- `TASK_RETENTION_DAYS`: 任务结果保留天数
- `MAX_CONCURRENT_TASKS_PER_USER`: 每用户最大并发任务数

## 快速开始

1. 复制配置文件：
```bash
cp CONFIG_EXAMPLE.md .env
```

2. 修改配置（根据实际环境调整）

3. 确保 Redis 已启动：
```bash
redis-server
```

4. 安装依赖：
```bash
pip install -r requirements.txt
```

5. 启动 Worker：
```bash
python -m app.services.tasks.worker
```

