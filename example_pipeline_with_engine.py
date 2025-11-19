"""
Pipeline 与 Engine 集成示例
展示如何在 Pipeline 中调用 Engine 进行实际的图像处理
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.image.pipelines.head_swap_pipeline import HeadSwapPipeline
from app.services.image.dto import EditTaskInput, HeadSwapConfig
from app.services.image.enums import EditMode, ImageQuality
from app.services.image.engines import get_engine_registry


def example_1_basic_pipeline_call():
    """示例 1: 基础 Pipeline 调用"""
    print("\n" + "=" * 50)
    print("示例 1: 基础 Pipeline 调用")
    print("=" * 50)
    
    # 创建 Pipeline 实例
    pipeline = HeadSwapPipeline()
    
    # 创建任务输入
    task_input = EditTaskInput(
        task_id="task_example_001",
        mode=EditMode.HEAD_SWAP,
        source_image="/path/to/source.jpg",  # 替换为实际路径
        config={
            "reference_image": "/path/to/reference.jpg",
            "quality": "high",
            "blend_strength": 0.8
        }
    )
    
    # 添加进度回调
    def progress_callback(progress: int, step: str):
        print(f"  [{progress}%] {step}")
    
    task_input.progress_callback = progress_callback
    
    print("\n开始执行换头 Pipeline...")
    
    try:
        # 执行 Pipeline
        result = pipeline.execute(task_input)
        
        if result.success:
            print(f"\n✅ Pipeline 执行成功！")
            print(f"   输出图片: {result.output_image}")
            print(f"   缩略图: {result.thumbnail}")
            print(f"   处理耗时: {result.processing_time:.2f} 秒")
        else:
            print(f"\n❌ Pipeline 执行失败: {result.error_message}")
            
    except Exception as e:
        print(f"\n❌ Pipeline 执行异常: {e}")


def example_2_pipeline_with_real_engine():
    """示例 2: Pipeline 调用真实 Engine"""
    print("\n" + "=" * 50)
    print("示例 2: Pipeline 调用真实 Engine")
    print("=" * 50)
    
    # 模拟一个简化的 Pipeline，展示如何调用 Engine
    class SimplePipeline:
        def __init__(self):
            # 获取 Engine 注册表
            self.registry = get_engine_registry()
        
        def process(self, source_image: str, reference_image: str):
            """处理流程"""
            
            # Step 1: 调用人脸检测 Engine
            print("\n[1/3] 调用人脸检测 Engine...")
            face_detection_engine = self.registry.get_engine("face_detection_api")
            
            if face_detection_engine:
                try:
                    faces = face_detection_engine.execute({
                        "image": source_image
                    })
                    print(f"     检测到 {len(faces.get('faces', []))} 张人脸")
                except Exception as e:
                    print(f"     ⚠️ 人脸检测失败: {e}")
            else:
                print("     ⚠️ 人脸检测 Engine 未配置")
            
            # Step 2: 调用人脸替换 Engine
            print("\n[2/3] 调用人脸替换 Engine...")
            face_swap_engine = self.registry.get_engine("face_swap_api")
            
            if face_swap_engine:
                try:
                    result = face_swap_engine.execute({
                        "source_image": source_image,
                        "reference_image": reference_image,
                        "blend_strength": 0.8
                    })
                    print(f"     ✅ 人脸替换完成")
                    output_image = result.get("output_image")
                except Exception as e:
                    print(f"     ⚠️ 人脸替换失败: {e}")
                    output_image = None
            else:
                print("     ⚠️ 人脸替换 Engine 未配置")
                output_image = None
            
            # Step 3: 保存结果
            print("\n[3/3] 保存结果...")
            if output_image:
                print(f"     结果已保存: {output_image}")
                return output_image
            else:
                print("     ⚠️ 没有可保存的结果")
                return None
    
    # 使用 Pipeline
    pipeline = SimplePipeline()
    result = pipeline.process(
        source_image="/path/to/source.jpg",
        reference_image="/path/to/reference.jpg"
    )
    
    if result:
        print(f"\n✅ 处理完成: {result}")
    else:
        print("\n⚠️ 处理未完成（可能是 Engine 未配置）")


def example_3_engine_registry_usage():
    """示例 3: Engine 注册表使用"""
    print("\n" + "=" * 50)
    print("示例 3: Engine 注册表使用")
    print("=" * 50)
    
    try:
        # 获取注册表
        registry = get_engine_registry()
        
        # 列出所有 Engine
        engines = registry.list_engines()
        print(f"\n已注册的 Engine: {len(engines)} 个")
        
        if engines:
            for engine_name in engines:
                engine = registry.get_engine(engine_name)
                print(f"\n  Engine: {engine_name}")
                print(f"    类型: {engine.engine_type.value}")
                print(f"    健康状态: {'✅' if engine.health_check() else '❌'}")
        else:
            print("\n  ⚠️ 没有注册任何 Engine")
            print("  请在 engine_config.yml 中配置 Engine")
        
        # 根据 Pipeline 和 Step 获取 Engine
        print("\n\n根据 Pipeline 步骤获取 Engine:")
        engine = registry.get_engine_for_step("head_swap", "face_detection")
        
        if engine:
            print(f"  head_swap.face_detection → {engine.engine_name}")
        else:
            print("  ⚠️ 未找到对应的 Engine")
        
    except Exception as e:
        print(f"❌ 注册表操作失败: {e}")


def example_4_mock_api_engine():
    """示例 4: 模拟 API Engine 调用"""
    print("\n" + "=" * 50)
    print("示例 4: 模拟 API Engine 调用（使用 httpbin.org）")
    print("=" * 50)
    
    from app.services.image.engines import ExternalApiEngine
    
    # 创建一个测试 Engine（使用 httpbin.org 作为测试端点）
    engine = ExternalApiEngine(config={
        "api_url": "https://httpbin.org/post",
        "api_key": "test_key_12345",
        "timeout": 10,
        "method": "POST",
        "auth_type": "Bearer"
    })
    
    print("\nEngine 配置:")
    print(f"  URL: {engine.api_url}")
    print(f"  Method: {engine.method}")
    print(f"  Timeout: {engine.timeout}秒")
    
    print("\n发送测试请求...")
    
    try:
        result = engine.execute({
            "task": "test_face_swap",
            "source": "image_data_here",
            "target": "reference_data_here"
        })
        
        print("\n✅ API 调用成功")
        print(f"\n响应数据:")
        
        # httpbin.org 会回显我们发送的数据
        request_json = result.get("json", {})
        print(f"  Task: {request_json.get('task')}")
        print(f"  Source: {request_json.get('source')}")
        print(f"  Target: {request_json.get('target')}")
        
        # 显示认证头
        headers = result.get("headers", {})
        auth_header = headers.get("Authorization", "")
        if auth_header:
            print(f"  Authorization: {auth_header[:30]}...")
        
    except Exception as e:
        print(f"\n❌ API 调用失败: {e}")


def example_5_image_io_utils():
    """示例 5: 图像 I/O 工具使用"""
    print("\n" + "=" * 50)
    print("示例 5: 图像 I/O 工具使用")
    print("=" * 50)
    
    from app.utils.image_io import (
        load_image,
        save_image,
        image_to_base64,
        base64_to_image,
        resize_image,
        create_thumbnail,
        get_image_info
    )
    from PIL import Image
    
    # 创建一个测试图片
    print("\n创建测试图片...")
    test_image = Image.new('RGB', (800, 600), color='blue')
    print(f"  尺寸: {test_image.size}")
    print(f"  模式: {test_image.mode}")
    
    # 转换为 base64
    print("\n转换为 Base64...")
    base64_str = image_to_base64(test_image, format="JPEG")
    print(f"  Base64 长度: {len(base64_str)} 字符")
    print(f"  前 50 字符: {base64_str[:50]}...")
    
    # 从 base64 还原
    print("\n从 Base64 还原图片...")
    restored_image = base64_to_image(base64_str)
    print(f"  尺寸: {restored_image.size}")
    print(f"  模式: {restored_image.mode}")
    
    # 调整大小
    print("\n调整图片大小...")
    resized = resize_image(restored_image, max_width=400, max_height=300)
    print(f"  原始尺寸: {restored_image.size}")
    print(f"  新尺寸: {resized.size}")
    
    # 创建缩略图
    print("\n创建缩略图...")
    thumbnail = create_thumbnail(restored_image, size=(128, 128))
    print(f"  缩略图尺寸: {thumbnail.size}")
    
    # 获取图片信息
    print("\n图片信息:")
    info = get_image_info(test_image)
    for key, value in info.items():
        print(f"  {key}: {value}")


def run_all_examples():
    """运行所有示例"""
    print("\n" + "🎨" * 25)
    print("Pipeline 与 Engine 集成示例")
    print("🎨" * 25)
    
    # 示例 1: 基础 Pipeline 调用（骨架）
    print("\n注意：示例 1 需要实际的图片文件路径")
    # example_1_basic_pipeline_call()
    
    # 示例 2: Pipeline 调用真实 Engine（需要配置）
    example_2_pipeline_with_real_engine()
    
    # 示例 3: Engine 注册表使用
    example_3_engine_registry_usage()
    
    # 示例 4: 模拟 API Engine 调用
    example_4_mock_api_engine()
    
    # 示例 5: 图像 I/O 工具
    example_5_image_io_utils()
    
    # 总结
    print("\n" + "=" * 50)
    print("✅ 所有示例完成！")
    print("=" * 50)
    print("\n关键要点:")
    print("1. Pipeline 通过 EngineRegistry 获取 Engine")
    print("2. Engine 负责实际的 AI 模型调用")
    print("3. 支持多种认证方式和重试机制")
    print("4. 图像自动编码/解码为 Base64")
    print("5. 配置驱动，易于切换和扩展")
    print("\n下一步:")
    print("• 在 engine_config.yml 中配置实际的 AI API")
    print("• 在 Pipeline 中调用 Engine 实现完整逻辑")
    print("• 准备 ComfyUI 工作流（如果使用本地模型）")


if __name__ == "__main__":
    run_all_examples()

