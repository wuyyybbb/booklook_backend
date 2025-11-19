# 🚀 Docker 快速启动指南

5 分钟快速启动 Formy Backend Docker 环境！

---

## 📋 前置要求

✅ 已安装 Docker Desktop  
✅ 已安装 Git  
✅ 有 Resend API Key（用于邮件功能）

---

## 🏠 本地快速启动

### 步骤 1: 克隆代码（如果还没有）

```bash
cd F:\formy\backend
```

### 步骤 2: 创建环境变量文件

```bash
# Windows PowerShell
Copy-Item .env.example .env
```

编辑 `.env` 文件，**必须修改以下值**：

```bash
# 修改这个！生成随机密钥
SECRET_KEY=your-super-secret-key-change-this-in-production

# 修改这个！填写你的 Resend API Key
RESEND_API_KEY=re_xxxxxxxxxxxxxxxxxxxxx
```

### 步骤 3: 启动服务

```bash
# 构建并启动所有服务（Backend + Redis + Worker）
docker-compose up -d --build
```

等待 1-2 分钟...

### 步骤 4: 验证

打开浏览器访问：

```
✅ API 文档: http://localhost:8000/docs
✅ 健康检查: http://localhost:8000/health
```

如果看到 `{"status": "healthy"}`，说明成功了！🎉

### 步骤 5: 查看日志（可选）

```bash
# 查看所有服务日志
docker-compose logs -f

# 仅查看 Backend 日志
docker-compose logs -f backend
```

### 停止服务

```bash
# 停止但保留数据
docker-compose stop

# 完全删除（包括数据）
docker-compose down -v
```

---

## ☁️ Render 部署快速指南

### 方法 1: 一键部署（使用 Blueprint）

1. **推送代码到 GitHub**

```bash
cd F:\formy\backend
git add .
git commit -m "Add Docker deployment files"
git push origin main
```

2. **登录 Render**

访问: https://dashboard.render.com/

3. **创建 Blueprint**

- 点击 **"New +"** → **"Blueprint"**
- 选择 `formy_backend` 仓库
- Render 会自动读取 `render.yaml` 并创建所有服务

4. **配置环境变量**

进入 **formy-backend** 服务，添加：

| 变量名 | 值 |
|--------|-----|
| `RESEND_API_KEY` | `re_xxxxxxxxxxxxx` |
| `CORS_ORIGINS` | `https://formy-frontend.vercel.app` |

5. **等待部署**

约 3-5 分钟，完成后访问：

```
https://formy-backend.onrender.com/health
```

看到 `{"status": "healthy"}` 就成功了！🎉

---

### 方法 2: 手动部署

1. **创建 Redis**
   - New + → Redis
   - Name: `formy-redis`
   - Plan: Free

2. **创建 Web Service**
   - New + → Web Service
   - Repository: `formy_backend`
   - Runtime: Docker
   - 添加环境变量（参考方法 1）

3. **部署完成**

---

## 🔧 常用命令

### 本地开发

```bash
# 启动
docker-compose up -d

# 重启
docker-compose restart backend

# 查看日志
docker-compose logs -f backend

# 停止
docker-compose down

# 进入容器
docker-compose exec backend bash
```

### 调试

```bash
# 检查容器状态
docker-compose ps

# 查看资源使用
docker stats

# 清理未使用的镜像
docker system prune -a
```

---

## ⚠️ 故障排查

### 问题 1: 端口已被占用

```
Error: Bind for 0.0.0.0:8000 failed: port is already allocated
```

**解决**：

```bash
# 查找占用端口的进程
netstat -ano | findstr :8000

# 停止现有的后端服务
docker-compose down
```

### 问题 2: Redis 连接失败

```
redis.exceptions.ConnectionError: Error connecting to Redis
```

**解决**：

```bash
# 重启 Redis
docker-compose restart redis

# 检查 Redis 是否运行
docker-compose ps redis
```

### 问题 3: 构建失败

```
ERROR: failed to solve: process "/bin/sh -c pip install..." did not complete successfully
```

**解决**：

```bash
# 清理缓存重新构建
docker-compose build --no-cache
docker-compose up -d
```

---

## 📊 服务端口

| 服务 | 端口 | 访问地址 |
|------|------|---------|
| Backend API | 8000 | http://localhost:8000 |
| Redis | 6379 | localhost:6379 |
| API 文档 | 8000 | http://localhost:8000/docs |

---

## ✅ 检查清单

### 启动前

- [ ] Docker Desktop 正在运行
- [ ] `.env` 文件已创建并配置
- [ ] `SECRET_KEY` 已修改
- [ ] `RESEND_API_KEY` 已填写

### 启动后

- [ ] `docker-compose ps` 显示所有服务 "Up"
- [ ] http://localhost:8000/health 返回 healthy
- [ ] http://localhost:8000/docs 可以访问
- [ ] Redis 可以连接（检查日志）

---

## 🎉 完成！

现在你可以：

1. 使用 API 文档测试接口: http://localhost:8000/docs
2. 配置前端连接到 Backend
3. 开始开发和测试

**需要帮助？**

- 查看完整文档: `DOCKER_DEPLOYMENT_GUIDE.md`
- 查看日志: `docker-compose logs -f`

