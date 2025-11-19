# 后端启动指南

## 快速启动

### 1. 安装依赖

```bash
cd backend
pip install -r requirements.txt
```

### 2. 启动服务

```bash
# 方式 1：直接运行
python -m app.main

# 方式 2：使用 uvicorn（推荐）
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 3. 验证服务

访问以下 URL 确认服务正常：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **根路径**: http://localhost:8000/

## 测试上传接口

### 使用 API 文档测试

1. 访问 http://localhost:8000/docs
2. 找到 `POST /api/v1/upload` 接口
3. 点击 "Try it out"
4. 选择一个图片文件
5. 点击 "Execute"
6. 查看响应

### 使用 curl 测试

```bash
curl -X POST "http://localhost:8000/api/v1/upload" \
  -H "accept: application/json" \
  -H "Content-Type: multipart/form-data" \
  -F "file=@test_image.jpg" \
  -F "purpose=source"
```

### 使用 Python 测试

```python
import requests

url = "http://localhost:8000/api/v1/upload"
files = {"file": open("test_image.jpg", "rb")}
data = {"purpose": "source"}

response = requests.post(url, files=files, data=data)
print(response.json())
```

## 目录结构

启动后会自动创建以下目录：

```
backend/
├── uploads/          # 上传文件存储
│   ├── source/       # 原图
│   └── reference/    # 参考图
└── results/          # 处理结果存储
```

## 环境变量

可以创建 `.env` 文件配置：

```env
APP_NAME=Formy
DEBUG=True
REDIS_HOST=localhost
REDIS_PORT=6379
```

## 常见问题

### 端口被占用

```bash
# 修改端口
uvicorn app.main:app --reload --port 8001
```

### 上传目录权限问题

```bash
chmod -R 755 uploads
chmod -R 755 results
```

### CORS 错误

检查 `app/core/config.py` 中的 `CORS_ORIGINS` 配置。

## 完整的服务列表

启动后可用的服务：

| 服务 | URL | 说明 |
|------|-----|------|
| API 文档 | http://localhost:8000/docs | Swagger UI |
| 健康检查 | http://localhost:8000/health | 服务状态 |
| 图片上传 | POST /api/v1/upload | 上传图片 |
| 静态文件（上传） | /uploads/* | 访问上传的图片 |
| 静态文件（结果） | /results/* | 访问处理结果 |

