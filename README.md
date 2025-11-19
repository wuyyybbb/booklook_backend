# 🎨 Formy Backend

AI 视觉创作工具后端服务 - 专为服装行业打造

---

## 📖 项目简介

Formy Backend 是一个基于 FastAPI 的 RESTful API 服务，提供：

- 🖼️ **图像上传与管理**
- 🔄 **AI 任务处理**（换头、换背景、换姿势）
- 👤 **用户认证**（邮箱验证码登录）
- 💳 **套餐与计费系统**
- 📊 **任务状态追踪**

---

## 🚀 快速开始

### 选择启动方式

#### 方式 1: Docker（推荐）

```bash
# 1. 配置环境变量
cp .env.example .env
# 编辑 .env 文件

# 2. 启动服务
docker-compose up -d

# 3. 访问
# http://localhost:8000/docs
```

📖 详细指南: [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md)

#### 方式 2: 本地开发

```bash
# 1. 安装依赖
pip install -r requirements.txt

# 2. 启动 Redis
# （需要单独安装 Redis）

# 3. 配置环境变量
cp .env.example .env

# 4. 启动服务
python -m uvicorn app.main:app --reload
```

📖 详细指南: [START_BACKEND.md](START_BACKEND.md)

---

## 📁 项目结构

```
backend/
├── app/                          # 应用代码
│   ├── api/                      # API 路由
│   │   └── v1/                   # API v1
│   │       ├── routes_upload.py  # 上传接口
│   │       ├── routes_tasks.py   # 任务接口
│   │       ├── routes_auth.py    # 认证接口
│   │       ├── routes_plans.py   # 套餐接口
│   │       └── routes_billing.py # 计费接口
│   ├── core/                     # 核心配置
│   │   └── config.py             # 应用配置
│   ├── models/                   # 数据模型
│   │   └── user.py               # 用户模型
│   ├── schemas/                  # Pydantic 模型
│   ├── services/                 # 业务逻辑
│   │   ├── auth/                 # 认证服务
│   │   ├── billing/              # 计费服务
│   │   ├── email/                # 邮件服务
│   │   ├── image/                # 图像处理
│   │   ├── storage/              # 存储服务
│   │   └── tasks/                # 任务管理
│   ├── utils/                    # 工具函数
│   ├── config/                   # 配置文件
│   └── main.py                   # 应用入口
├── uploads/                      # 上传文件目录
├── Dockerfile                    # Docker 镜像配置
├── docker-compose.yml            # Docker Compose 配置
├── render.yaml                   # Render 部署配置
├── requirements.txt              # Python 依赖
└── .env.example                  # 环境变量示例

```

---

## 🔧 技术栈

- **框架**: FastAPI 0.104+
- **Python**: 3.10+
- **数据库**: Redis（任务队列 + 状态管理）
- **认证**: JWT (PyJWT)
- **邮件**: Resend
- **图像处理**: Pillow
- **服务器**: Gunicorn + Uvicorn Workers
- **容器化**: Docker + Docker Compose

---

## 🌐 API 文档

启动服务后访问：

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

### 核心接口

| 端点 | 方法 | 说明 |
|------|------|------|
| `/api/v1/upload` | POST | 上传图片 |
| `/api/v1/tasks` | POST | 创建 AI 任务 |
| `/api/v1/tasks/{id}` | GET | 查询任务状态 |
| `/api/v1/auth/send-code` | POST | 发送验证码 |
| `/api/v1/auth/login` | POST | 登录 |
| `/api/v1/plans` | GET | 获取套餐列表 |
| `/api/v1/billing/me` | GET | 获取用户计费信息 |

---

## ⚙️ 环境变量

### 必需配置

| 变量 | 说明 | 示例 |
|------|------|------|
| `SECRET_KEY` | JWT 签名密钥 | `random-secret-key` |
| `RESEND_API_KEY` | Resend API 密钥 | `re_xxxxxx` |
| `REDIS_HOST` | Redis 主机地址 | `localhost` |

### 可选配置

查看 `.env.example` 了解所有可配置项。

---

## 🐳 Docker 部署

### 本地测试

```bash
# 启动所有服务（Backend + Redis + Worker）
docker-compose up -d

# 查看日志
docker-compose logs -f backend

# 停止服务
docker-compose down
```

### 生产部署（Render）

1. 推送代码到 GitHub
2. 在 Render 中创建 Blueprint
3. 配置环境变量
4. 自动部署完成

📖 完整指南: [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md)

---

## 📚 文档

| 文档 | 说明 |
|------|------|
| [DOCKER_QUICK_START.md](DOCKER_QUICK_START.md) | Docker 快速启动（5 分钟） |
| [DOCKER_DEPLOYMENT_GUIDE.md](DOCKER_DEPLOYMENT_GUIDE.md) | Docker 完整部署指南 |
| [START_BACKEND.md](START_BACKEND.md) | 本地开发启动指南 |
| [ARCHITECTURE.md](ARCHITECTURE.md) | 系统架构设计 |
| [TASK_SYSTEM_README.md](TASK_SYSTEM_README.md) | 任务系统文档 |
| [PIPELINE_README.md](PIPELINE_README.md) | Pipeline 层文档 |
| [ENGINE_USAGE_GUIDE.md](ENGINE_USAGE_GUIDE.md) | Engine 层使用指南 |

---

## 🧪 测试

```bash
# 运行测试脚本
python test_task_system.py
python test_engines.py
python test_plans_api.py
python test_billing_api.py
python test_credits_integration.py
```

---

## 🔒 安全注意事项

### 生产环境必做

- [ ] 修改 `SECRET_KEY` 为随机强密钥
- [ ] 使用 HTTPS
- [ ] 配置防火墙规则
- [ ] 定期更新依赖包
- [ ] 启用速率限制
- [ ] 配置日志监控

### 敏感信息

**不要将以下内容提交到 Git：**

- `.env` 文件
- API 密钥
- 密码和 Token
- 用户上传的图片

---

## 📊 性能优化

### 推荐配置

| 资源 | 开发环境 | 生产环境 |
|------|---------|---------|
| CPU | 2 核 | 2-4 核 |
| 内存 | 2 GB | 4-8 GB |
| Workers | 1 | CPU 核心数 * 2 + 1 |
| Redis | 本地 | 托管服务 |

### Gunicorn Workers

```bash
# 计算公式
Workers = (CPU 核心数 * 2) + 1

# 例如 2 核 CPU
Workers = (2 * 2) + 1 = 5
```

---

## 🐛 常见问题

### Redis 连接失败

```bash
# 检查 Redis 是否运行
docker-compose ps redis

# 重启 Redis
docker-compose restart redis
```

### 邮件发送失败

1. 检查 `RESEND_API_KEY` 是否正确
2. 确认发件邮箱已在 Resend 中验证
3. 查看 Resend Dashboard 中的日志

### 端口被占用

```bash
# Windows 查找占用端口的进程
netstat -ano | findstr :8000

# 停止进程或更换端口
```

---

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

---

## 📄 许可证

MIT License

---

## 📮 联系方式

- **GitHub**: https://github.com/wuyyybbb/formy_backend
- **Email**: support@formy.it.com

---

## 🎉 致谢

感谢以下开源项目：

- [FastAPI](https://fastapi.tiangolo.com/)
- [Redis](https://redis.io/)
- [Gunicorn](https://gunicorn.org/)
- [Docker](https://www.docker.com/)

---

**Happy Coding! 🚀**

