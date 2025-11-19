# 🐳 Formy Backend Docker 部署指南

完整的 Docker 部署方案，支持本地开发和 Render 生产环境。

---

## 📋 目录

1. [环境要求](#环境要求)
2. [本地 Docker 开发](#本地-docker-开发)
3. [Render 平台部署](#render-平台部署)
4. [环境变量配置](#环境变量配置)
5. [常见问题](#常见问题)

---

## 🔧 环境要求

### 必需软件

- **Docker Desktop** (Windows/Mac) 或 **Docker Engine** (Linux)
  - 下载地址: https://www.docker.com/products/docker-desktop
  - 版本要求: Docker 20.10+, Docker Compose 2.0+

- **Git**（用于克隆代码）

### 验证安装

```bash
docker --version
# 输出: Docker version 24.0.x

docker-compose --version
# 输出: Docker Compose version v2.x.x
```

---

## 🏠 本地 Docker 开发

### 方法 1: 使用 Docker Compose（推荐）

包含 Backend + Redis + Worker 完整环境。

#### 1. 创建环境变量文件

```bash
cd F:\formy\backend
cp .env.example .env
```

编辑 `.env` 文件，填写必要的配置：

```bash
# .env
APP_NAME=Formy API
APP_VERSION=1.0.0
DEBUG=false

# Redis 配置
REDIS_HOST=redis
REDIS_PORT=6379
REDIS_DB=0

# JWT 配置
SECRET_KEY=your-super-secret-key-change-this-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=43200

# 邮件配置
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
FROM_EMAIL=support@formy.it.com

# CORS 配置
CORS_ORIGINS=http://localhost:3000,http://localhost:5173
```

#### 2. 启动所有服务

```bash
# 构建并启动
docker-compose up --build

# 或者在后台运行
docker-compose up -d --build
```

#### 3. 验证服务

打开浏览器访问：

- **API 文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **Redis**: localhost:6379

#### 4. 查看日志

```bash
# 查看所有服务日志
docker-compose logs -f

# 查看特定服务日志
docker-compose logs -f backend
docker-compose logs -f redis
docker-compose logs -f worker
```

#### 5. 停止服务

```bash
# 停止但保留数据
docker-compose stop

# 停止并删除容器（数据卷保留）
docker-compose down

# 停止并删除所有数据
docker-compose down -v
```

---

### 方法 2: 单独构建 Docker 镜像

仅构建 Backend 镜像，Redis 需要单独运行。

#### 1. 构建镜像

```bash
cd F:\formy\backend

# 构建镜像
docker build -t formy-backend:latest .

# 查看镜像
docker images | grep formy-backend
```

#### 2. 运行容器

```bash
# 启动 Redis（如果还没运行）
docker run -d --name redis -p 6379:6379 redis:7-alpine

# 启动 Backend
docker run -d \
  --name formy-backend \
  -p 8000:8000 \
  -e REDIS_HOST=host.docker.internal \
  -e REDIS_PORT=6379 \
  -e SECRET_KEY=your-secret-key \
  -e RESEND_API_KEY=your-resend-key \
  formy-backend:latest

# 查看日志
docker logs -f formy-backend
```

#### 3. 停止容器

```bash
docker stop formy-backend redis
docker rm formy-backend redis
```

---

## ☁️ Render 平台部署

Render 是一个现代化的云平台，支持 Docker 部署，提供免费套餐。

### 方案 1: 使用 Blueprint（推荐）

Blueprint 允许通过 `render.yaml` 文件自动配置所有服务。

#### 1. 准备代码

确保以下文件已提交到 GitHub：

```
backend/
├── Dockerfile
├── .dockerignore
├── render.yaml
├── requirements.txt
├── app/
└── ...
```

#### 2. 连接 GitHub

1. 登录 [Render Dashboard](https://dashboard.render.com/)
2. 点击右上角 **"New +"** → **"Blueprint"**
3. 选择 **"Connect a repository"**
4. 授权 GitHub，选择 `formy_backend` 仓库

#### 3. 应用 Blueprint

Render 会自动读取 `render.yaml` 并创建以下服务：

- ✅ **Web Service**: formy-backend（Docker 容器）
- ✅ **Redis**: formy-redis（托管 Redis）

#### 4. 配置环境变量

在 Render Dashboard 中，进入 **formy-backend** 服务：

1. 点击 **"Environment"** 标签
2. 添加/修改以下环境变量：

| 变量名 | 值 | 说明 |
|--------|-----|------|
| `RESEND_API_KEY` | `re_xxxxxx` | Resend API 密钥 |
| `FROM_EMAIL` | `support@formy.it.com` | 发件邮箱 |
| `CORS_ORIGINS` | `https://formy-frontend.vercel.app` | 前端域名 |
| `SECRET_KEY` | （自动生成） | JWT 密钥 |

3. 点击 **"Save Changes"**

#### 5. 部署

Render 会自动构建和部署！

- 构建时间：约 3-5 分钟
- 部署完成后会获得一个 URL: `https://formy-backend.onrender.com`

#### 6. 验证部署

访问以下 URL 验证：

```
✅ https://formy-backend.onrender.com/health
✅ https://formy-backend.onrender.com/docs
✅ https://formy-backend.onrender.com/
```

---

### 方案 2: 手动创建服务

如果不使用 Blueprint，可以手动创建。

#### 1. 创建 Redis 服务

1. 登录 Render Dashboard
2. 点击 **"New +"** → **"Redis"**
3. 配置：
   - **Name**: `formy-redis`
   - **Plan**: Free
   - **Region**: Oregon (US West)
4. 点击 **"Create Redis"**
5. 记录 Redis 的 **Internal URL**（类似 `redis://red-xxxxx:6379`）

#### 2. 创建 Web Service

1. 点击 **"New +"** → **"Web Service"**
2. 选择 **"Connect a repository"**
3. 选择 `formy_backend` 仓库
4. 配置：
   - **Name**: `formy-backend`
   - **Runtime**: **Docker**
   - **Region**: Oregon (US West)
   - **Branch**: `main`
   - **Dockerfile Path**: `./Dockerfile`
   - **Docker Build Context**: `.`
5. 添加环境变量（参考上方表格）
6. 点击 **"Create Web Service"**

---

## ⚙️ 环境变量配置

### 必需环境变量

| 变量名 | 说明 | 示例值 |
|--------|------|--------|
| `REDIS_HOST` | Redis 主机地址 | `localhost` / `redis` / `red-xxxxx` |
| `REDIS_PORT` | Redis 端口 | `6379` |
| `SECRET_KEY` | JWT 签名密钥 | `随机生成的长字符串` |
| `RESEND_API_KEY` | Resend API 密钥 | `re_xxxxxxxxxxxxx` |
| `FROM_EMAIL` | 发件邮箱地址 | `support@formy.it.com` |

### 可选环境变量

| 变量名 | 说明 | 默认值 |
|--------|------|--------|
| `APP_NAME` | 应用名称 | `Formy API` |
| `APP_VERSION` | 应用版本 | `1.0.0` |
| `DEBUG` | 调试模式 | `false` |
| `REDIS_DB` | Redis 数据库编号 | `0` |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token 过期时间（分钟） | `43200`（30天） |
| `CORS_ORIGINS` | 允许的前端域名 | `http://localhost:3000` |
| `WORKERS` | Gunicorn Worker 数量 | `2` |

---

## 🔍 常见问题

### 1. 构建失败：`gcc: not found`

**原因**：缺少 C 编译器，Pillow 需要编译。

**解决**：Dockerfile 已包含 `gcc` 安装，确保使用提供的 Dockerfile。

---

### 2. Redis 连接失败

**本地开发**：

```bash
# 检查 Redis 是否运行
docker ps | grep redis

# 如果没有运行，启动 Redis
docker-compose up -d redis
```

**Render 部署**：

- 检查 `REDIS_HOST` 环境变量是否正确配置
- 使用 Render 提供的 **Internal URL**

---

### 3. Health Check 失败

**检查**：

```bash
# 本地测试
curl http://localhost:8000/health

# 或在浏览器中访问
http://localhost:8000/health
```

**Render 部署**：

- 在 Render Dashboard 查看 **Logs** 标签
- 检查是否有启动错误

---

### 4. CORS 错误

**症状**：前端请求被浏览器阻止。

**解决**：

1. 检查 `CORS_ORIGINS` 环境变量
2. 确保包含前端的完整 URL（包括协议和端口）

```bash
# 本地开发
CORS_ORIGINS=http://localhost:3000,http://localhost:5173

# 生产环境
CORS_ORIGINS=https://formy-frontend.vercel.app
```

---

### 5. 镜像体积过大

**优化方法**：

1. 使用 `python:3.10-slim` 而非 `python:3.10`（已应用）
2. 使用 `.dockerignore` 排除不必要的文件（已应用）
3. 清理 apt 缓存（已应用）

**当前镜像大小**：约 300-400 MB

---

### 6. Render Free Plan 限制

**限制**：

- ⚠️ 15 分钟无活动后自动休眠
- ⚠️ 每月 750 小时免费（足够单个服务 24/7 运行）
- ⚠️ 冷启动时间：30-60 秒

**解决方法**：

- 使用 **Cron Job** 或 **UptimeRobot** 定期 ping 健康检查端点
- 升级到付费计划（$7/月起）

---

## 📊 部署对比

| 特性 | 本地 Docker | Render Free | Render Paid |
|------|-------------|-------------|-------------|
| **成本** | 免费 | 免费 | $7/月起 |
| **性能** | 取决于本机 | 有限 | 高性能 |
| **自动部署** | ❌ | ✅ | ✅ |
| **自定义域名** | ❌ | ✅ | ✅ |
| **SSL 证书** | ❌ | ✅ 自动 | ✅ 自动 |
| **休眠** | ❌ | ✅ 15分钟 | ❌ |
| **数据库备份** | 手动 | ❌ | ✅ |

---

## 🚀 快速命令参考

### 本地开发

```bash
# 启动所有服务
docker-compose up -d

# 重新构建并启动
docker-compose up --build -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down

# 进入容器
docker-compose exec backend bash
```

### 镜像管理

```bash
# 构建镜像
docker build -t formy-backend .

# 查看镜像
docker images

# 删除镜像
docker rmi formy-backend

# 清理未使用的镜像
docker image prune -a
```

### 调试

```bash
# 进入运行中的容器
docker exec -it formy-backend bash

# 查看容器详细信息
docker inspect formy-backend

# 查看资源使用
docker stats formy-backend
```

---

## ✅ 部署检查清单

### 部署前

- [ ] 所有代码已提交到 GitHub
- [ ] `Dockerfile` 已创建并测试
- [ ] `.dockerignore` 已配置
- [ ] `render.yaml` 已配置（如果使用 Blueprint）
- [ ] 环境变量已准备好
- [ ] 本地 Docker 测试通过

### 部署后

- [ ] 健康检查端点正常 (`/health`)
- [ ] API 文档可访问 (`/docs`)
- [ ] Redis 连接正常
- [ ] 邮件服务配置正确
- [ ] CORS 配置正确
- [ ] 前端能正常调用后端 API

---

## 🎉 完成！

恭喜！你已经成功部署 Formy Backend 到 Docker 环境。

**下一步**：

1. 更新前端的 API Base URL
2. 配置自定义域名（可选）
3. 设置监控和日志（可选）

**有问题？**

- 查看 Render Logs: Dashboard → Service → Logs
- 查看本地日志: `docker-compose logs -f`
- 参考 Render 文档: https://render.com/docs

