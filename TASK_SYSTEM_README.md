# Task / Redis / Worker 任务系统骨架

## 📋 概述

这是 Formy 项目的任务系统骨架代码，实现了基于 Redis 的任务队列和 Worker 处理机制。

## 🏗️ 架构设计

```
┌─────────────┐
│   API 层    │  创建任务 → TaskService
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ TaskService │  业务逻辑层（任务管理）
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ TaskQueue   │  Redis 队列层（入队/出队/状态更新）
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ Redis 队列  │  FIFO 任务队列 + Hash 存储
└──────┬──────┘
       │
       ↓
┌─────────────┐
│ TaskWorker  │  Worker 循环消费任务
└──────┬──────┘
       │
       ↓
┌─────────────┐
│  Pipeline   │  具体的图像处理流程（待实现）
└─────────────┘
```

## 📁 文件结构

```
backend/app/
├── schemas/
│   └── task.py                    # 任务数据模型（TaskStatus, EditMode, TaskInfo）
│
├── services/tasks/
│   ├── __init__.py                # 模块导出
│   ├── manager.py                 # TaskService - 任务管理服务
│   ├── queue.py                   # TaskQueue - Redis 队列操作
│   └── worker.py                  # TaskWorker - Worker 工作进程
│
├── core/
│   └── config.py                  # 应用配置（Redis、文件存储等）
│
└── utils/
    └── id_generator.py            # ID 生成工具
```

## 🔧 核心组件

### 1. TaskQueue（队列层）

**职责**：封装 Redis 操作，管理任务队列和状态

**主要方法**：
- `push_task(task_id, task_data)` - 推送任务到队列
- `pop_task(timeout)` - 从队列弹出任务（阻塞式）
- `get_task_data(task_id)` - 获取任务数据
- `update_task_status(task_id, status, ...)` - 更新任务状态
- `cancel_task(task_id)` - 取消任务

**Redis 数据结构**：
```
# 任务队列（List）
formy:task:queue → [task_1, task_2, task_3]

# 任务数据（Hash）
formy:task:data:task_20231117_abc123 → {
    task_id: "task_20231117_abc123"
    status: "processing"
    data: "{...}"
    progress: "50"
    created_at: "2025-11-17T10:00:00"
    updated_at: "2025-11-17T10:00:30"
}

# 处理中任务集合（Set）
formy:task:processing → {task_1, task_2}
```

---

### 2. TaskService（服务层）

**职责**：提供任务管理的业务逻辑

**主要方法**：
- `create_task(request)` - 创建任务
- `get_task(task_id)` - 获取任务详情
- `get_task_list(...)` - 获取任务列表
- `cancel_task(task_id)` - 取消任务
- `update_task_progress(task_id, progress, step)` - 更新进度
- `complete_task(task_id, result)` - 标记完成
- `fail_task(task_id, error)` - 标记失败

---

### 3. TaskWorker（Worker 层）

**职责**：循环消费队列中的任务并分发处理

**工作流程**：
1. 从 Redis 队列获取任务（阻塞式）
2. 更新任务状态为 `processing`
3. 根据模式分发到对应 Pipeline
4. 更新任务进度
5. 标记任务完成或失败

**优雅关闭**：
- 支持 `SIGINT` (Ctrl+C) 和 `SIGTERM` 信号
- 当前任务处理完成后才退出

---

## 🎯 任务状态流转

```
pending → processing → done
                    ↘ failed
                    ↘ cancelled
```

| 状态 | 说明 | 可能的下一状态 |
|------|------|---------------|
| `pending` | 已入队待处理 | processing, cancelled |
| `processing` | 处理中 | done, failed |
| `done` | 成功完成 | - |
| `failed` | 处理失败 | - |
| `cancelled` | 已取消 | - |

---

## 🚀 使用示例

### 1. 创建任务

```python
from app.services.tasks import get_task_service
from app.schemas.task import TaskCreateRequest, EditMode

task_service = get_task_service()

# 创建换头任务
request = TaskCreateRequest(
    mode=EditMode.HEAD_SWAP,
    source_image="img_20231117_abc123",
    config={
        "reference_image": "img_20231117_def456",
        "quality": "high",
        "blend_strength": 0.8
    }
)

task_info = task_service.create_task(request)
print(f"任务已创建: {task_info.task_id}")
```

### 2. 查询任务状态

```python
task_info = task_service.get_task("task_20231117_xyz789")

if task_info:
    print(f"状态: {task_info.status}")
    print(f"进度: {task_info.progress}%")
    
    if task_info.status == "done":
        print(f"结果: {task_info.result.output_image}")
    elif task_info.status == "failed":
        print(f"错误: {task_info.error.message}")
```

### 3. 启动 Worker

```bash
# 方式1：直接运行
python -m app.services.tasks.worker

# 方式2：作为模块导入
python
>>> from app.services.tasks import run_worker
>>> run_worker()
```

### 4. 取消任务

```python
success = task_service.cancel_task("task_20231117_xyz789")
if success:
    print("任务已取消")
```

---

## 🔌 依赖配置

### 1. Redis 配置

在 `.env` 文件或环境变量中配置：

```env
REDIS_HOST=localhost
REDIS_PORT=6379
REDIS_DB=0
REDIS_PASSWORD=  # 可选
```

### 2. Python 依赖

```bash
pip install redis
pip install pydantic
pip install pydantic-settings
```

---

## ⚙️ 配置说明

### settings 配置项

| 配置项 | 默认值 | 说明 |
|--------|--------|------|
| `REDIS_HOST` | localhost | Redis 主机地址 |
| `REDIS_PORT` | 6379 | Redis 端口 |
| `REDIS_DB` | 0 | Redis 数据库编号 |
| `TASK_RETENTION_DAYS` | 7 | 任务结果保留天数 |
| `MAX_CONCURRENT_TASKS_PER_USER` | 3 | 每用户最大并发任务数 |

---

## 📊 监控和调试

### 获取队列统计

```python
stats = task_service.get_queue_stats()
print(f"待处理: {stats['pending']}")
print(f"处理中: {stats['processing']}")
print(f"总任务数: {stats['total_tasks']}")
```

### 查看 Redis 数据

```bash
# 连接 Redis
redis-cli

# 查看队列长度
LLEN formy:task:queue

# 查看任务数据
HGETALL formy:task:data:task_20231117_abc123

# 查看处理中任务
SMEMBERS formy:task:processing
```

---

## 🔄 与 Pipeline 集成（待实现）

当前 Worker 中的 Pipeline 调用是骨架代码，实际使用时需要：

1. 实现具体的 Pipeline 类（`HeadSwapPipeline`, `BackgroundPipeline`, `PoseChangePipeline`）
2. 在 Worker 的 `_dispatch_to_pipeline` 方法中调用实际 Pipeline
3. Pipeline 负责调用 Engine（闭源 API 或 ComfyUI）

示例：
```python
# 在 worker.py 中
def _process_head_swap(self, task_id, source_image, config):
    from app.services.image.pipelines import HeadSwapPipeline
    
    pipeline = HeadSwapPipeline()
    result = pipeline.execute(
        source_image=source_image,
        config=config,
        progress_callback=lambda p, s: self.task_service.update_task_progress(task_id, p, s)
    )
    
    return result
```

---

## ⚠️ 注意事项

1. **Redis 必须运行**：Worker 启动前会检查 Redis 连接
2. **任务幂等性**：同一任务不应重复处理（通过 task_id 确保唯一性）
3. **错误处理**：Worker 异常不会导致进程退出，会继续处理下一个任务
4. **并发控制**：当前为单 Worker 模式，可启动多个 Worker 实例实现并发
5. **任务超时**：当前未实现超时机制，长时间处理可能需要额外监控

---

## 🎯 下一步开发

- [ ] 实现 Pipeline 层（换头/换背景/换姿势）
- [ ] 实现 Engine 层（API 调用/ComfyUI 集成）
- [ ] 添加任务超时机制
- [ ] 添加任务重试机制
- [ ] 实现任务优先级
- [ ] 添加 WebSocket 实时推送
- [ ] 实现任务清理定时器
- [ ] 添加性能监控和日志

---

## 📝 更新日志

| 版本 | 日期 | 说明 |
|------|------|------|
| v1.0 | 2025-11-17 | 初始骨架版本 |

