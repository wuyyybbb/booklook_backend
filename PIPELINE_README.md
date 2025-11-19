# Pipeline 与 Engine 架构文档

## 📋 概述

Pipeline 层是 Formy 的图像处理核心，负责将复杂的 AI 图像编辑流程封装成清晰的业务逻辑。Engine 层则负责实际调用底层 AI 模型（闭源 API 或 ComfyUI 工作流）。

## 🏗️ 架构设计

```
┌─────────────────────────────────────────────────────────────┐
│                    ImageEditService                          │
│                   （统一入口服务）                              │
└───────────────────────┬─────────────────────────────────────┘
                        │
        ┌───────────────┼───────────────┐
        │               │               │
        ↓               ↓               ↓
┌───────────────┐ ┌───────────────┐ ┌───────────────┐
│ HeadSwap      │ │ Background    │ │ PoseChange    │
│ Pipeline      │ │ Pipeline      │ │ Pipeline      │
└───────┬───────┘ └───────┬───────┘ └───────┬───────┘
        │                 │                 │
        └─────────────────┼─────────────────┘
                          │
                          ↓
                ┌─────────────────┐
                │ EngineRegistry  │
                │  （引擎注册表）    │
                └────────┬────────┘
                         │
        ┌────────────────┼────────────────┐
        │                │                │
        ↓                ↓                ↓
┌──────────────┐  ┌──────────────┐  ┌──────────────┐
│ ExternalApi  │  │ ComfyUI      │  │ LocalModel   │
│ Engine       │  │ Engine       │  │ Engine       │
└──────────────┘  └──────────────┘  └──────────────┘
```

## 📁 文件结构

```
backend/app/services/image/
│
├── enums.py                           # ✅ 枚举定义
├── dto.py                             # ✅ 数据传输对象
├── edit_service.py                    # ✅ 图像编辑服务（统一入口）
│
├── pipelines/                         # ✅ Pipeline 层
│   ├── __init__.py
│   ├── base.py                        # ✅ Pipeline 基类
│   ├── head_swap_pipeline.py          # ✅ 换头 Pipeline
│   ├── background_pipeline.py         # ✅ 换背景 Pipeline
│   └── pose_change_pipeline.py        # ✅ 换姿势 Pipeline
│
└── engines/                           # ✅ Engine 层
    ├── __init__.py
    ├── base.py                        # ✅ Engine 基类
    ├── external_api.py                # ✅ 外部 API Engine
    ├── comfyui_engine.py              # ✅ ComfyUI Engine
    └── registry.py                    # ✅ Engine 注册表

backend/
├── engine_config.yml                  # ✅ Engine 配置文件
```

## 🎯 核心组件

### 1. ImageEditService（统一入口）

**职责**：作为外部调用 Pipeline 的统一入口

```python
from app.services.image.edit_service import get_image_edit_service
from app.services.image.dto import EditTaskInput
from app.services.image.enums import EditMode

service = get_image_edit_service()

task_input = EditTaskInput(
    task_id="task_123",
    mode=EditMode.HEAD_SWAP,
    source_image="/path/to/source.jpg",
    config={
        "reference_image": "/path/to/reference.jpg",
        "quality": "high"
    }
)

result = service.execute_edit(task_input)
```

---

### 2. PipelineBase（Pipeline 基类）

**提供的通用功能**：
- ✅ 计时功能（`_start_timer()`, `_get_elapsed_time()`）
- ✅ 进度更新（`_update_progress()`）
- ✅ 结果构建（`_create_success_result()`, `_create_error_result()`）
- ✅ 日志记录（`_log_step()`）

**子类必须实现的方法**：
- `execute(task_input)` - 执行 Pipeline
- `validate_input(task_input)` - 验证输入

---

### 3. HeadSwapPipeline（换头 Pipeline）

**处理流程**：
1. 加载原始图片和参考图片（10%）
2. 检测人脸（30%）
3. 提取人脸特征（50%）
4. 替换人脸（70%）
5. 融合优化（90%）
6. 保存结果（100%）

**配置参数**：
```python
{
    "reference_image": "img_123",      # 参考头像
    "quality": "high",                 # 质量等级
    "preserve_details": true,          # 保留细节
    "blend_strength": 0.8              # 融合强度
}
```

---

### 4. BackgroundPipeline（换背景 Pipeline）

**处理流程**：
1. 加载原始图片（10%）
2. 人像分割（30%）
3. 移除背景（50%）
4. 准备新背景（60%）
5. 合成图像（75%）
6. 边缘优化（90%）
7. 保存结果（100%）

**配置参数**：
```python
{
    "background_type": "custom",       # custom/preset/remove
    "background_image": "img_456",     # 自定义背景
    "edge_blur": 2,                    # 边缘羽化
    "color_match": true                # 颜色匹配
}
```

---

### 5. PoseChangePipeline（换姿势 Pipeline）

**处理流程**：
1. 加载原始图片（10%）
2. 检测源姿态（25%）
3. 获取目标姿态（40%）
4. 提取关键点（55%）
5. 姿势迁移（75%）
6. 优化结果（90%）
7. 保存结果（100%）

**配置参数**：
```python
{
    "target_pose": "standing_front",   # 预设姿势
    "pose_reference": "img_789",       # 或参考图片
    "preserve_face": true,             # 保持面部
    "smoothness": 0.7                  # 平滑度
}
```

---

### 6. EngineBase（Engine 基类）

**提供的通用功能**：
- ✅ 配置管理（`get_config()`）
- ✅ 健康检查（`health_check()`）
- ✅ 日志记录（`_log()`）

**子类必须实现的方法**：
- `execute(input_data)` - 执行引擎处理
- `validate_input(input_data)` - 验证输入

---

### 7. ExternalApiEngine（外部 API Engine）

**功能**：调用闭源模型 API

**配置示例**：
```yaml
engines:
  face_swap_api:
    type: external_api
    config:
      api_url: "https://api.example.com/face-swap"
      api_key: "${FACE_SWAP_API_KEY}"
      timeout: 60
```

**使用方法**：
```python
from app.services.image.engines import get_engine_registry

registry = get_engine_registry()
engine = registry.get_engine("face_swap_api")

result = engine.execute(input_data={
    "source_image": "base64_encoded_image",
    "target_image": "base64_encoded_image"
})
```

---

### 8. ComfyUIEngine（ComfyUI Engine）

**功能**：调用本地 ComfyUI 工作流

**配置示例**：
```yaml
engines:
  comfyui_head_swap:
    type: comfyui
    config:
      comfyui_url: "http://localhost:8188"
      workflow_path: "./workflows/head_swap_workflow.json"
      timeout: 300
```

**工作流程**：
1. 加载工作流定义（JSON）
2. 注入输入数据到工作流节点
3. 提交工作流到 ComfyUI
4. 等待执行完成
5. 获取输出图片

---

### 9. EngineRegistry（引擎注册表）

**功能**：管理所有 Engine，提供配置驱动的引擎选择

**使用方法**：
```python
from app.services.image.engines import get_engine_registry

# 获取注册表实例
registry = get_engine_registry()

# 获取特定引擎
engine = registry.get_engine("face_swap_api")

# 根据 Pipeline 和 Step 获取引擎
engine = registry.get_engine_for_step("head_swap", "face_detection")

# 列出所有引擎
engines = registry.list_engines()

# 健康检查
health = registry.health_check_all()
```

---

## 📊 数据流

### 完整的任务处理流程

```
1. Worker 获取任务
   ↓
2. 调用 ImageEditService.execute_edit()
   ↓
3. 根据 mode 选择对应 Pipeline
   ↓
4. Pipeline.execute(task_input)
   ↓
5. Pipeline 各步骤依次执行
   ├─ 加载图片
   ├─ 调用 Engine 处理（通过 EngineRegistry）
   ├─ 更新进度
   └─ 保存结果
   ↓
6. 返回 EditTaskResult
   ↓
7. Worker 更新任务状态
```

---

## 🔧 配置文件详解

### engine_config.yml 结构

```yaml
# Engine 定义
engines:
  <engine_name>:
    type: <external_api|comfyui|local_model>
    config:
      <engine_specific_config>

# Pipeline 配置
pipelines:
  <pipeline_name>:
    enabled: <true|false>
    steps:
      <step_name>:
        engine: <engine_name>
        description: <step_description>

# 全局配置
global:
  retry:
    max_attempts: 3
  timeout:
    default: 60
```

---

## 🚀 使用示例

### 示例 1: 在 Worker 中调用 Pipeline

```python
# worker.py
from app.services.image.edit_service import get_image_edit_service
from app.services.image.dto import EditTaskInput

def _process_head_swap(self, task_id, source_image, config):
    # 创建任务输入
    task_input = EditTaskInput(
        task_id=task_id,
        mode=EditMode.HEAD_SWAP,
        source_image=source_image,
        config=config,
        progress_callback=lambda p, s: self.task_service.update_task_progress(task_id, p, s)
    )
    
    # 执行编辑
    edit_service = get_image_edit_service()
    result = edit_service.execute_edit(task_input)
    
    if result.success:
        return {
            "output_image": result.output_image,
            "thumbnail": result.thumbnail,
            "metadata": result.metadata
        }
    else:
        raise Exception(result.error_message)
```

### 示例 2: 添加新的 Engine

```python
# 1. 创建新的 Engine 类
from app.services.image.engines.base import EngineBase

class CustomEngine(EngineBase):
    def execute(self, input_data, **kwargs):
        # 实现处理逻辑
        pass
    
    def validate_input(self, input_data):
        # 实现验证逻辑
        return True

# 2. 在 engine_config.yml 中配置
engines:
  custom_engine:
    type: custom
    config:
      api_url: "..."

# 3. 在 EngineRegistry 中注册
registry.engine_classes["custom"] = CustomEngine
```

### 示例 3: 扩展 Pipeline

```python
# 创建新的 Pipeline
from app.services.image.pipelines.base import PipelineBase

class CustomPipeline(PipelineBase):
    def execute(self, task_input):
        self._start_timer()
        # 实现处理流程
        return self._create_success_result(output_image="...")
    
    def validate_input(self, task_input):
        return True
```

---

## ⚠️ 当前状态（骨架）

### ✅ 已完成
- Pipeline 基类和三个 Pipeline 的函数框架
- Engine 基类和两种 Engine 的函数框架
- EngineRegistry 配置驱动机制
- ImageEditService 统一入口
- 完整的数据模型（DTO）
- 配置文件示例

### ❌ 待实现（内部逻辑）
- Pipeline 中的实际图像处理逻辑
- Engine 中的实际 API 调用逻辑
- ComfyUI 工作流集成
- 图像 I/O 工具
- 实际的 AI 模型对接

---

## 📝 下一步开发

### P0 - 核心功能
1. 实现图像 I/O 工具（`utils/image_io.py`）
2. 对接一个闭源 API（如人脸检测）
3. 测试 ExternalApiEngine 实际调用
4. 完善一个 Pipeline 的完整逻辑（如 HeadSwapPipeline）

### P1 - ComfyUI 集成
5. 实现 ComfyUI 工作流加载和提交
6. 实现 ComfyUI 任务状态轮询
7. 测试 ComfyUIEngine 实际调用
8. 创建示例工作流 JSON

### P2 - 完善和优化
9. 错误处理和重试机制
10. 日志系统集成
11. 性能监控
12. 单元测试

---

## 🎯 设计亮点

### 1. 分层解耦
- Pipeline 层：业务逻辑
- Engine 层：技术实现
- 两层互不干扰，易于扩展

### 2. 配置驱动
- 通过 YAML 配置管理 Engine
- 无需修改代码即可切换 Engine
- 支持环境变量

### 3. 进度追踪
- Pipeline 实时更新进度
- 通过回调函数通知外部
- 前端可实时显示进度

### 4. 统一接口
- 所有 Pipeline 继承自 PipelineBase
- 所有 Engine 继承自 EngineBase
- 统一的调用方式

### 5. 单例模式
- ImageEditService 单例
- EngineRegistry 单例
- 避免重复初始化

---

## 📚 参考资料

- [FastAPI 官方文档](https://fastapi.tiangolo.com/)
- [Pydantic 官方文档](https://docs.pydantic.dev/)
- [ComfyUI GitHub](https://github.com/comfyanonymous/ComfyUI)

---

**文档版本**: v1.0  
**更新时间**: 2025-11-17

