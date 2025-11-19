# 任务系统架构图

## 整体架构

```
┌─────────────────────────────────────────────────────────────────┐
│                         前端 (React)                              │
│                 上传图片 / 选择模式 / 轮询状态                      │
└───────────────────────────┬─────────────────────────────────────┘
                            │ HTTP REST API
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                      API 层 (FastAPI)                             │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ POST /tasks  │  │ GET /tasks   │  │ DELETE /task │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   服务层 (TaskService)                            │
│  • create_task()      创建任务                                     │
│  • get_task()         查询任务                                     │
│  • cancel_task()      取消任务                                     │
│  • update_progress()  更新进度                                     │
│  • complete_task()    标记完成                                     │
│  • fail_task()        标记失败                                     │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                   队列层 (TaskQueue)                              │
│  • push_task()        推入队列                                     │
│  • pop_task()         弹出队列 (阻塞)                              │
│  • update_status()    更新状态                                     │
│  • get_task_data()    获取数据                                     │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                         Redis                                    │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ formy:task:queue (List)                                 │     │
│  │ [task_1, task_2, task_3, ...]                          │     │
│  └────────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ formy:task:data:task_xxx (Hash)                        │     │
│  │ { task_id, status, data, progress, ... }              │     │
│  └────────────────────────────────────────────────────────┘     │
│  ┌────────────────────────────────────────────────────────┐     │
│  │ formy:task:processing (Set)                            │     │
│  │ {task_1, task_2}                                       │     │
│  └────────────────────────────────────────────────────────┘     │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Worker 进程                                   │
│  while True:                                                     │
│    task_id = queue.pop_task()  # 阻塞式获取                       │
│    task_data = queue.get_task_data(task_id)                     │
│    result = dispatch_to_pipeline(task_data)                     │
│    queue.update_status(task_id, "done", result)                 │
└───────────────────────────┬─────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                    Pipeline 层（待实现）                           │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │ HeadSwap     │  │ Background   │  │ PoseChange   │          │
│  │ Pipeline     │  │ Pipeline     │  │ Pipeline     │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
└─────────┼──────────────────┼──────────────────┼─────────────────┘
          │                  │                  │
          └──────────────────┼──────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────────────┐
│                     Engine 层（待实现）                            │
│  ┌──────────────────┐            ┌──────────────────┐           │
│  │ ExternalApi      │            │ ComfyUI          │           │
│  │ Engine           │            │ Engine           │           │
│  │ (闭源模型调用)     │            │ (本地工作流)      │           │
│  └──────────────────┘            └──────────────────┘           │
└─────────────────────────────────────────────────────────────────┘
```

## 任务生命周期

```
┌─────────┐
│ 创建任务  │
└────┬────┘
     │
     ↓
┌─────────────────┐
│ pending         │  ← 已入队，等待处理
│ progress: 0%    │
└────┬────────────┘
     │
     │ Worker 获取任务
     ↓
┌─────────────────┐
│ processing      │  ← 处理中
│ progress: 30%   │
│ "正在检测人脸..."  │
└────┬────────────┘
     │
     │ Pipeline 处理
     ↓
┌─────────────────┐
│ processing      │
│ progress: 60%   │
│ "正在替换头部..."  │
└────┬────────────┘
     │
     │ 完成或失败
     ↓
┌─────────────────┐        ┌─────────────────┐
│ done            │   OR   │ failed          │
│ progress: 100%  │        │ error: {...}    │
│ result: {...}   │        └─────────────────┘
└─────────────────┘
```

## Redis 数据结构详解

### 1. 任务队列 (List)

```
Key: formy:task:queue
Type: List
用途: FIFO 任务队列

数据示例:
["task_20231117_abc123", "task_20231117_abc124", "task_20231117_abc125"]

操作:
- RPUSH: 推入新任务（尾部）
- BLPOP: 弹出任务（头部，阻塞式）
- LLEN: 获取队列长度
- LREM: 移除特定任务（取消任务时）
```

### 2. 任务数据 (Hash)

```
Key: formy:task:data:{task_id}
Type: Hash
用途: 存储任务的详细信息

数据示例:
{
  "task_id": "task_20231117_abc123",
  "status": "processing",
  "data": "{\"mode\": \"HEAD_SWAP\", \"source_image\": \"img_123\", ...}",
  "progress": "60",
  "current_step": "正在进行头部融合...",
  "created_at": "2025-11-17T10:00:00",
  "updated_at": "2025-11-17T10:00:30",
  "result": null,
  "error": null
}

操作:
- HSET: 创建/更新任务数据
- HGETALL: 获取完整任务信息
- HGET: 获取单个字段
- DEL: 删除任务数据
```

### 3. 处理中任务集合 (Set)

```
Key: formy:task:processing
Type: Set
用途: 追踪当前正在处理的任务（用于监控）

数据示例:
{"task_20231117_abc123", "task_20231117_abc125"}

操作:
- SADD: Worker 获取任务时添加
- SREM: 任务完成/失败/取消时移除
- SCARD: 获取处理中任务数量
- SMEMBERS: 获取所有处理中任务
```

## 状态转换矩阵

| 当前状态 | 操作 | 新状态 | 触发者 |
|---------|------|--------|--------|
| - | create_task | pending | API/用户 |
| pending | pop_task | processing | Worker |
| pending | cancel_task | cancelled | API/用户 |
| processing | update_progress | processing | Worker/Pipeline |
| processing | complete_task | done | Worker/Pipeline |
| processing | fail_task | failed | Worker/Pipeline |
| done | - | - | - |
| failed | - | - | - |
| cancelled | - | - | - |

## 模块依赖关系

```
API 路由 (routes_tasks.py)
    ↓ 依赖
TaskService (manager.py)
    ↓ 依赖
TaskQueue (queue.py)
    ↓ 依赖
Redis 客户端
    ↓ 依赖
Redis 服务器

Worker (worker.py)
    ↓ 依赖
TaskQueue + TaskService
    ↓ 依赖
Pipeline (待实现)
    ↓ 依赖
Engine (待实现)
```

## 并发处理模型

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  Worker 1   │     │  Worker 2   │     │  Worker 3   │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       └───────────────────┼───────────────────┘
                           ↓
                   ┌───────────────┐
                   │  Redis 队列    │
                   │  (原子操作)     │
                   └───────────────┘
                           ↑
                           │
                   ┌───────┴───────┐
                   │   任务来源     │
                   │  (API 创建)    │
                   └───────────────┘

特点:
• 多个 Worker 可并发消费
• Redis BLPOP 保证原子性
• 无需额外锁机制
• 自动负载均衡
```

## 错误处理流程

```
Worker 处理任务
    ↓
    ├─→ Pipeline 异常
    │       ↓
    │   捕获异常
    │       ↓
    │   fail_task(error_code, message, details)
    │       ↓
    │   更新 Redis: status=failed, error={...}
    │       ↓
    │   从 processing Set 移除
    │       ↓
    │   继续处理下一个任务
    │
    ├─→ Engine 异常（同上）
    │
    └─→ Worker 异常
            ↓
        捕获异常
            ↓
        fail_task("INTERNAL_ERROR", ...)
            ↓
        记录日志
            ↓
        继续处理下一个任务

特点:
• 异常不会导致 Worker 退出
• 所有错误都会更新到 Redis
• 前端可查询错误信息
• 失败任务可人工重试（待实现）
```

## 性能优化点

### 1. 阻塞式队列消费
```python
# ❌ 轮询方式（低效）
while True:
    task = redis.lpop("queue")
    if task:
        process(task)
    time.sleep(0.1)  # 空转浪费 CPU

# ✅ 阻塞式方式（高效）
while True:
    task = redis.blpop("queue", timeout=5)  # 阻塞等待
    if task:
        process(task)
```

### 2. Hash 存储任务数据
```python
# ❌ String 存储（需要反复序列化）
redis.set(f"task:{id}", json.dumps(data))
data = json.loads(redis.get(f"task:{id}"))

# ✅ Hash 存储（可单独更新字段）
redis.hset(f"task:{id}", "status", "processing")
redis.hset(f"task:{id}", "progress", "50")
```

### 3. Set 追踪处理中任务
```python
# 快速查询处理中任务数量
count = redis.scard("formy:task:processing")

# 快速判断任务是否在处理
is_processing = redis.sismember("formy:task:processing", task_id)
```

## 扩展性考虑

### 水平扩展 Worker
```
可启动多个 Worker 实例：
• 同一台机器上启动多个进程
• 不同机器上启动多个进程
• Docker 容器中启动多个副本
• Kubernetes Deployment (replicas: N)

无需修改代码，Redis BLPOP 自动分发
```

### 任务优先级（可扩展）
```
增加多个队列：
formy:task:queue:high      # 高优先级
formy:task:queue:normal    # 普通优先级
formy:task:queue:low       # 低优先级

Worker 优先消费高优先级队列
```

### 任务类型路由（可扩展）
```
按任务类型分队列：
formy:task:queue:head_swap       # 换头任务
formy:task:queue:background      # 换背景任务
formy:task:queue:pose_change     # 换姿势任务

不同 Worker 消费不同队列
```

---

**文档版本**: v1.0  
**更新时间**: 2025-11-17

