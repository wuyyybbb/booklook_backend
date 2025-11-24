# Render Worker 部署指南

本指南说明如何在 Render 上配置 Background Worker 来处理 AI 任务。

## 📋 前置条件

1. ✅ 后端代码已推送到 GitHub (`wuyyybbb/formy_backend`)
2. ✅ Web Service 已部署并运行正常
3. ✅ Redis 实例已创建并配置

---

## 🚀 方案选择

### **方案 A：创建独立的 Background Worker（推荐）**

**优点：**
- 资源隔离，API 和 Worker 互不影响
- 可以独立扩展 Worker 实例
- 更稳定，Worker 崩溃不影响 API

**缺点：**
- 需要额外的 Render 实例费用

---

### **方案 B：在 Web Service 中同时运行 API 和 Worker**

**优点：**
- 不需要额外费用
- 配置简单

**缺点：**
- Worker 可能占用 API 资源
- 不便于扩展

---

## 📝 方案 A：创建独立 Background Worker（推荐）

### 步骤 1：创建 Background Worker

1. 登录 Render Dashboard: https://dashboard.render.com
2. 点击 **"New +"** → **"Background Worker"**
3. 选择仓库：`wuyyybbb/formy_backend`
4. 配置如下：

```yaml
Name: formy-worker
Environment: Python 3
Region: Singapore (或选择距离用户最近的)
Branch: main
Build Command: pip install -r requirements.txt
Start Command: python run_worker_pipeline.py
```

### 步骤 2：复制环境变量

从 Web Service 复制以下环境变量到 Worker：

| 环境变量名 | 说明 | 示例 |
|----------|------|------|
| `REDIS_URL` | Redis 连接地址 | 从 Render Redis 获取 |
| `COMFYUI_URL` | ComfyUI 服务地址 | `https://d5m-dbdcym9t4h0p6ianf-qdkzkd4d-custom.service.onethingrobot.com` |
| `SECRET_KEY` | JWT 密钥 | 与 Web Service 保持一致 |
| `UPLOAD_DIR` | 上传目录 | `./uploads` |
| `RESULT_DIR` | 结果目录 | `./results` |

### 步骤 3：部署

1. 点击 **"Create Background Worker"**
2. 等待构建和部署完成（约 3-5 分钟）
3. 查看 Logs，确认 Worker 启动成功

**成功的 Logs 应该显示：**
```
[Worker] Pipeline Worker 已启动，等待任务...
[Worker] 将调用真实的 ComfyUI Pipeline 处理任务
[Worker] 按 Ctrl+C 停止
[成功] Redis 连接正常
```

---

## 📝 方案 B：在 Web Service 中同时运行

### 修改 Web Service 启动命令

1. 进入 Render Dashboard → `formy_backend` Web Service
2. 点击 **"Settings"**
3. 找到 **"Start Command"**
4. 修改为：

```bash
python run_worker_pipeline.py & python -m uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

5. 保存并重新部署

---

## 🔍 验证 Worker 是否正常工作

### 1. 查看 Logs

在 Render Dashboard 中查看 Worker 的 Logs：

```
[Worker] 获取到任务: task_xxxxx
[Worker] 任务模式: POSE_CHANGE
[Worker] 开始执行换姿势 Pipeline...
[Worker] 进度: 10% - 正在加载图片...
[Worker] 进度: 30% - 正在调用 AI 引擎...
[Worker] ✅ 任务完成
```

### 2. 前端测试

1. 登录前端：https://formy-frontend.vercel.app
2. 上传图片并创建任务
3. 查看任务状态是否从 `pending` → `processing` → `done`
4. 查看是否生成了结果图片

---

## ⚠️ 常见问题

### 问题 1：Worker 无法连接到 Redis

**症状：**
```
❌ Redis 连接失败: Connection refused
```

**解决方案：**
1. 确认 Worker 环境变量中有 `REDIS_URL`
2. 确认 `REDIS_URL` 使用的是 **Internal Key Value URL**（不是 External）
3. 重新部署 Worker

---

### 问题 2：Worker 无法连接到 ComfyUI

**症状：**
```
❌ ComfyUI 执行失败: Connection timeout
```

**解决方案：**
1. 确认 `COMFYUI_URL` 环境变量正确
2. 测试 ComfyUI 是否在线：
   ```bash
   curl https://d5m-dbdcym9t4h0p6ianf-qdkzkd4d-custom.service.onethingrobot.com/system_stats
   ```
3. 确认 onethingai 的 GPU 实例正在运行

---

### 问题 3：任务一直卡在 pending 状态

**可能原因：**
1. Worker 没有启动
2. Worker 启动了但崩溃了
3. Redis 队列没有正确配置

**解决方案：**
1. 查看 Worker Logs，确认是否在运行
2. 手动重启 Worker
3. 检查 Web Service 和 Worker 使用的是同一个 Redis

---

### 问题 4：Worker 处理任务后崩溃

**症状：**
```
[Worker] ❌ Pipeline 执行异常: ...
```

**解决方案：**
1. 查看完整的错误堆栈
2. 确认 `workflows/pose_swap_workflow.json` 文件存在
3. 确认 ComfyUI 工作流定义正确
4. 检查图片文件是否存在

---

## 📊 监控 Worker 健康状态

### 查看 Worker 状态

在 Render Dashboard 中：
1. 进入 Worker 服务
2. 查看 **"Status"** 指示器
3. 查看 **"Metrics"**（CPU、内存使用情况）

### 查看任务处理速度

在 Logs 中搜索：
```
✅ 任务完成
```

统计每小时完成的任务数量。

---

## 🔄 扩展 Worker

如果任务处理速度不够快，可以增加 Worker 实例数量：

1. 在 Render Dashboard 中进入 Worker 服务
2. 点击 **"Settings"** → **"Scaling"**
3. 增加 **"Number of Instances"**

**注意：** 多个 Worker 会同时消费同一个 Redis 队列，自动实现负载均衡。

---

## 📚 相关文档

- [Render Background Workers 文档](https://render.com/docs/background-workers)
- [Render Redis 文档](https://render.com/docs/redis)
- [ComfyUI API 文档](https://github.com/comfyanonymous/ComfyUI)

---

## 🆘 需要帮助？

如果遇到问题，请查看：
1. Worker Logs
2. Web Service Logs
3. Redis 连接状态
4. ComfyUI 服务状态

记录完整的错误信息以便排查。

