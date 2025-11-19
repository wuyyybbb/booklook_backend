# Engine 使用指南

## 📋 概述

Engine 层是 Formy 中负责实际调用 AI 模型的模块。目前支持两种 Engine：
- **ExternalApiEngine** - 调用闭源 API（如商业 AI 服务）
- **ComfyUIEngine** - 调用本地 ComfyUI 工作流

---

## 🚀 快速开始

### 1. ExternalApiEngine 使用示例

#### 基础配置

```python
from app.services.image.engines import ExternalApiEngine

# 创建 Engine 实例
engine = ExternalApiEngine(config={
    "api_url": "https://api.example.com/face-swap",
    "api_key": "your_api_key_here",
    "timeout": 60,
    "method": "POST",
    "auth_type": "Bearer"
})

# 调用 API
result = engine.execute({
    "source_image": "/path/to/source.jpg",  # 会自动转换为 base64
    "target_image": "/path/to/target.jpg"
})

print(result)
```

#### 高级配置

```python
engine = ExternalApiEngine(config={
    "api_url": "https://api.example.com/process",
    "api_key": "your_api_key",
    
    # 请求配置
    "method": "POST",                    # GET 或 POST
    "timeout": 60,                       # 超时时间（秒）
    "auth_type": "Bearer",               # Bearer / ApiKey / Custom
    
    # 重试配置
    "retry_times": 3,                    # 重试次数
    "retry_delay": 2,                    # 重试延迟（秒）
    
    # 图像处理
    "encode_images": True,               # 自动编码图片为 base64
    
    # 响应解析
    "result_key": "result",              # 从响应中提取的结果字段
    "decode_result": False,              # 是否解码 base64 结果
    
    # 额外参数
    "extra_params": {
        "model": "v2",
        "quality": "high"
    }
})
```

---

### 2. ComfyUIEngine 使用示例

#### 基础配置

```python
from app.services.image.engines import ComfyUIEngine

# 创建 Engine 实例
engine = ComfyUIEngine(config={
    "comfyui_url": "http://localhost:8188",
    "workflow_path": "./workflows/face_swap.json",
    "timeout": 300
})

# 执行工作流
result = engine.execute({
    "input_image": "/path/to/input.jpg",
    "reference_image": "/path/to/reference.jpg"
})

print(result)
```

#### 工作流 JSON 准备

ComfyUI 工作流 JSON 示例（`workflows/face_swap.json`）：

```json
{
    "1": {
        "class_type": "LoadImage",
        "inputs": {
            "image": "input.jpg"
        }
    },
    "2": {
        "class_type": "FaceSwap",
        "inputs": {
            "source_image": ["1", 0],
            "target_face": "reference.jpg"
        }
    },
    "3": {
        "class_type": "SaveImage",
        "inputs": {
            "images": ["2", 0],
            "filename_prefix": "result"
        }
    }
}
```

---

### 3. 使用 EngineRegistry（推荐）

#### 配置文件方式

`engine_config.yml`:

```yaml
engines:
  face_swap_api:
    type: external_api
    config:
      api_url: "https://api.example.com/face-swap"
      api_key: "${FACE_SWAP_API_KEY}"  # 从环境变量读取
      timeout: 60
      
  background_removal_api:
    type: external_api
    config:
      api_url: "https://api.remove.bg/v1.0/removebg"
      api_key: "${REMOVE_BG_API_KEY}"
      auth_type: "Custom"
      auth_header: "X-Api-Key"
      
  comfyui_pose:
    type: comfyui
    config:
      comfyui_url: "http://localhost:8188"
      workflow_path: "./workflows/pose_transfer.json"
      timeout: 300
```

#### 使用注册表

```python
from app.services.image.engines import get_engine_registry

# 获取注册表（自动加载配置）
registry = get_engine_registry()

# 获取特定 Engine
face_swap_engine = registry.get_engine("face_swap_api")
bg_removal_engine = registry.get_engine("background_removal_api")

# 使用 Engine
result = face_swap_engine.execute({
    "source_image": "/path/to/source.jpg",
    "target_image": "/path/to/target.jpg"
})
```

---

## 🔧 在 Pipeline 中使用 Engine

### 示例：在 HeadSwapPipeline 中调用 Engine

```python
# head_swap_pipeline.py

from app.services.image.pipelines.base import PipelineBase
from app.services.image.engines import get_engine_registry

class HeadSwapPipeline(PipelineBase):
    
    def __init__(self):
        super().__init__()
        # 获取 Engine 注册表
        self.registry = get_engine_registry()
    
    def _detect_face(self, image_path: str):
        """检测人脸"""
        # 获取人脸检测 Engine
        engine = self.registry.get_engine("face_detection_api")
        
        if not engine:
            raise Exception("人脸检测 Engine 未配置")
        
        # 调用 Engine
        result = engine.execute({
            "image": image_path
        })
        
        return result
    
    def _swap_face(self, source_image: str, reference_image: str):
        """替换人脸"""
        # 获取人脸替换 Engine
        engine = self.registry.get_engine("face_swap_api")
        
        if not engine:
            raise Exception("人脸替换 Engine 未配置")
        
        # 调用 Engine
        result = engine.execute({
            "source_image": source_image,
            "reference_image": reference_image,
            "blend_strength": 0.8
        })
        
        return result
```

---

## 📊 常见 AI API 对接示例

### 1. Remove.bg（背景移除）

```python
engine = ExternalApiEngine(config={
    "api_url": "https://api.remove.bg/v1.0/removebg",
    "api_key": "your_remove_bg_key",
    "method": "POST",
    "auth_type": "Custom",
    "auth_header": "X-Api-Key",
    "result_key": "data.result_b64"
})

result = engine.execute({
    "image_file_b64": image_to_base64("/path/to/image.jpg"),
    "size": "auto",
    "format": "png"
})
```

### 2. Replicate API（通用）

```python
engine = ExternalApiEngine(config={
    "api_url": "https://api.replicate.com/v1/predictions",
    "api_key": "your_replicate_token",
    "method": "POST",
    "auth_type": "Bearer",
    "timeout": 120
})

result = engine.execute({
    "version": "model_version_hash",
    "input": {
        "image": "https://example.com/image.jpg",
        "scale": 2
    }
})
```

### 3. Stability AI

```python
engine = ExternalApiEngine(config={
    "api_url": "https://api.stability.ai/v1/generation/stable-diffusion-xl/image-to-image",
    "api_key": "your_stability_key",
    "method": "POST",
    "auth_type": "Bearer",
    "timeout": 180
})

result = engine.execute({
    "init_image": image_to_base64("/path/to/init.jpg"),
    "prompt": "a professional photo",
    "strength": 0.5
})
```

---

## 🎨 图像处理工具

### 图像 I/O 工具

```python
from app.utils.image_io import (
    load_image,
    save_image,
    image_to_base64,
    base64_to_image,
    resize_image,
    create_thumbnail
)

# 加载图片
image = load_image("/path/to/image.jpg")

# 转换为 base64
base64_str = image_to_base64(image)

# 从 base64 还原
image = base64_to_image(base64_str)

# 调整大小
resized = resize_image(image, max_width=1024, max_height=1024)

# 创建缩略图
thumbnail = create_thumbnail(image, size=(256, 256))

# 保存图片
save_image(thumbnail, "/path/to/output.jpg", quality=90)
```

---

## ⚙️ Engine 配置选项

### ExternalApiEngine 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `api_url` | string | 必填 | API 端点地址 |
| `api_key` | string | - | API 密钥 |
| `method` | string | POST | HTTP 方法（GET/POST） |
| `timeout` | int | 60 | 超时时间（秒） |
| `auth_type` | string | Bearer | 认证类型（Bearer/ApiKey/Custom） |
| `auth_header` | string | Authorization | 认证请求头名称 |
| `retry_times` | int | 3 | 重试次数 |
| `retry_delay` | int | 2 | 重试延迟（秒） |
| `encode_images` | bool | True | 自动编码图片为 base64 |
| `result_key` | string | result | 结果字段名 |
| `decode_result` | bool | False | 解码 base64 结果 |
| `extra_params` | dict | {} | 额外请求参数 |

### ComfyUIEngine 配置

| 配置项 | 类型 | 默认值 | 说明 |
|--------|------|--------|------|
| `comfyui_url` | string | http://localhost:8188 | ComfyUI 服务地址 |
| `workflow_path` | string | 必填 | 工作流 JSON 文件路径 |
| `timeout` | int | 300 | 超时时间（秒） |
| `poll_interval` | int | 2 | 轮询间隔（秒） |

---

## 🐛 错误处理

### 捕获 Engine 异常

```python
try:
    result = engine.execute(input_data)
except ValueError as e:
    # 输入验证错误
    print(f"输入错误: {e}")
except TimeoutError as e:
    # 超时错误
    print(f"请求超时: {e}")
except Exception as e:
    # 其他错误
    print(f"Engine 执行失败: {e}")
```

### 健康检查

```python
# 检查单个 Engine
if not engine.health_check():
    print("Engine 不可用")

# 检查所有 Engine
registry = get_engine_registry()
health = registry.health_check_all()

for name, is_healthy in health.items():
    print(f"{name}: {'✅' if is_healthy else '❌'}")
```

---

## 🧪 测试

运行 Engine 测试：

```bash
cd backend
python test_engines.py
```

测试内容包括：
- ExternalApiEngine 基础功能
- ComfyUIEngine 基础功能
- EngineRegistry 注册和查询
- 图像 Base64 编码/解码

---

## 📝 最佳实践

### 1. 使用环境变量管理 API Key

`.env`:
```env
FACE_SWAP_API_KEY=your_key_here
REMOVE_BG_API_KEY=your_key_here
```

`engine_config.yml`:
```yaml
engines:
  face_swap:
    type: external_api
    config:
      api_url: "https://api.example.com/face-swap"
      api_key: "${FACE_SWAP_API_KEY}"
```

### 2. 合理设置超时和重试

```python
config = {
    "timeout": 120,      # 较慢的 AI 模型需要更长超时
    "retry_times": 3,    # 网络不稳定时增加重试
    "retry_delay": 5     # 增加重试延迟避免限流
}
```

### 3. 图片预处理

```python
# 在发送到 API 前，调整图片大小以减少传输时间
from app.utils.image_io import load_image, resize_image, image_to_base64

image = load_image("/path/to/large_image.jpg")
resized = resize_image(image, max_width=1024, max_height=1024)
base64_str = image_to_base64(resized)
```

### 4. 使用 EngineRegistry 统一管理

```python
# 推荐：通过配置文件管理
registry = get_engine_registry()
engine = registry.get_engine("face_swap_api")

# 不推荐：直接创建实例
# engine = ExternalApiEngine(config={...})
```

---

## 🔗 相关文档

- [Pipeline 使用文档](PIPELINE_README.md)
- [架构设计文档](ARCHITECTURE.md)
- [API 规范文档](../docs/API_SPEC.md)

---

**文档版本**: v1.0  
**更新时间**: 2025-11-17
