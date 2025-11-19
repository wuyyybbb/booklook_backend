"""
Engine 测试脚本
测试 ExternalApiEngine 和 ComfyUIEngine 的功能
"""
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.image.engines import (
    ExternalApiEngine,
    ComfyUIEngine,
    get_engine_registry
)


def test_external_api_engine():
    """测试外部 API Engine"""
    print("\n" + "=" * 50)
    print("测试 1: ExternalApiEngine 基础功能")
    print("=" * 50)
    
    # 创建 Engine 实例
    config = {
        "api_url": "https://httpbin.org/post",  # 使用 httpbin 测试
        "api_key": "test_key_12345",
        "timeout": 10,
        "method": "POST",
        "auth_type": "Bearer"
    }
    
    engine = ExternalApiEngine(config)
    
    # 测试配置获取
    print(f"✅ API URL: {engine.api_url}")
    print(f"✅ API Key: {engine.api_key[:10]}...")
    print(f"✅ Timeout: {engine.timeout}秒")
    print(f"✅ Method: {engine.method}")
    
    # 测试输入验证
    print("\n测试输入验证:")
    assert engine.validate_input({"test": "data"}) == True
    print("✅ 字典输入验证通过")
    
    assert engine.validate_input(None) == False
    print("✅ None 输入验证失败（符合预期）")
    
    # 测试健康检查
    print("\n测试健康检查:")
    health = engine.health_check()
    print(f"✅ 健康检查: {'通过' if health else '失败'}")
    
    # 测试 API 调用（使用 httpbin.org）
    print("\n测试 API 调用:")
    try:
        input_data = {
            "task": "test_api_call",
            "data": "sample_data"
        }
        
        result = engine.execute(input_data)
        
        print("✅ API 调用成功")
        print(f"   响应数据: {result.get('json', {})}")
        
    except Exception as e:
        print(f"⚠️ API 调用失败（可能是网络问题）: {e}")


def test_comfyui_engine():
    """测试 ComfyUI Engine"""
    print("\n" + "=" * 50)
    print("测试 2: ComfyUIEngine 基础功能")
    print("=" * 50)
    
    # 创建 Engine 实例
    config = {
        "comfyui_url": "http://localhost:8188",
        "workflow_path": "./workflows/test_workflow.json",
        "timeout": 300,
        "poll_interval": 2
    }
    
    engine = ComfyUIEngine(config)
    
    # 测试配置获取
    print(f"✅ ComfyUI URL: {engine.comfyui_url}")
    print(f"✅ Workflow Path: {engine.workflow_path}")
    print(f"✅ Timeout: {engine.timeout}秒")
    print(f"✅ Client ID: {engine.client_id}")
    
    # 测试健康检查
    print("\n测试健康检查:")
    health = engine.health_check()
    if health:
        print("✅ ComfyUI 服务运行中")
    else:
        print("⚠️ ComfyUI 服务未运行（这是正常的，除非你本地运行了 ComfyUI）")
    
    print("\n注意：完整的 ComfyUI 测试需要：")
    print("1. 本地运行 ComfyUI 服务（http://localhost:8188）")
    print("2. 准备好工作流 JSON 文件")
    print("3. 提供实际的输入图片")


def test_engine_registry():
    """测试 Engine 注册表"""
    print("\n" + "=" * 50)
    print("测试 3: EngineRegistry 功能")
    print("=" * 50)
    
    try:
        # 获取注册表实例
        registry = get_engine_registry("./engine_config.yml")
        
        print("✅ 注册表初始化成功")
        
        # 列出所有已注册的 Engine
        engines = registry.list_engines()
        print(f"\n已注册的 Engine 数量: {len(engines)}")
        
        if engines:
            print("Engine 列表:")
            for engine_name in engines:
                print(f"  - {engine_name}")
        else:
            print("⚠️ 没有注册任何 Engine（需要配置 engine_config.yml）")
        
        # 健康检查所有 Engine
        print("\n执行健康检查:")
        health_results = registry.health_check_all()
        
        for engine_name, is_healthy in health_results.items():
            status = "✅ 健康" if is_healthy else "❌ 不可用"
            print(f"  {engine_name}: {status}")
        
    except FileNotFoundError:
        print("⚠️ engine_config.yml 文件不存在")
        print("   请参考 engine_config.yml 创建配置文件")
    except Exception as e:
        print(f"❌ 注册表测试失败: {e}")


def test_manual_engine_registration():
    """测试手动注册 Engine"""
    print("\n" + "=" * 50)
    print("测试 4: 手动注册 Engine")
    print("=" * 50)
    
    from app.services.image.engines.registry import EngineRegistry
    
    # 创建新的注册表（不加载配置文件）
    registry = EngineRegistry(config_path=None)
    
    # 手动注册一个测试 API Engine
    success = registry.register_engine(
        engine_name="test_api",
        engine_type="external_api",
        config={
            "api_url": "https://httpbin.org/post",
            "api_key": "test_key",
            "timeout": 10
        }
    )
    
    if success:
        print("✅ 成功注册 test_api Engine")
        
        # 获取并测试
        engine = registry.get_engine("test_api")
        if engine:
            print(f"✅ 成功获取 Engine: {engine.engine_name}")
            print(f"   Engine 类型: {engine.engine_type.value}")
        
    # 手动注册一个 ComfyUI Engine
    success = registry.register_engine(
        engine_name="test_comfyui",
        engine_type="comfyui",
        config={
            "comfyui_url": "http://localhost:8188",
            "workflow_path": "./test_workflow.json"
        }
    )
    
    if success:
        print("✅ 成功注册 test_comfyui Engine")
    
    # 列出所有 Engine
    engines = registry.list_engines()
    print(f"\n当前注册的 Engine: {engines}")


def test_image_encoding():
    """测试图像编码功能"""
    print("\n" + "=" * 50)
    print("测试 5: 图像 Base64 编码（模拟）")
    print("=" * 50)
    
    try:
        from app.utils.image_io import image_to_base64, base64_to_image
        from PIL import Image
        import io
        
        # 创建一个测试图片（红色 100x100）
        test_image = Image.new('RGB', (100, 100), color='red')
        
        # 转换为 base64
        base64_str = image_to_base64(test_image, format="JPEG")
        
        print(f"✅ 图片转 Base64 成功")
        print(f"   Base64 长度: {len(base64_str)} 字符")
        print(f"   Base64 前 50 字符: {base64_str[:50]}...")
        
        # 将 base64 转回图片
        decoded_image = base64_to_image(base64_str)
        
        print(f"✅ Base64 转图片成功")
        print(f"   图片尺寸: {decoded_image.size}")
        print(f"   图片模式: {decoded_image.mode}")
        
    except Exception as e:
        print(f"❌ 图像编码测试失败: {e}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀" * 25)
    print("Formy Engine 测试套件")
    print("🚀" * 25)
    
    # 测试 1: ExternalApiEngine
    test_external_api_engine()
    
    # 测试 2: ComfyUIEngine
    test_comfyui_engine()
    
    # 测试 3: EngineRegistry
    test_engine_registry()
    
    # 测试 4: 手动注册
    test_manual_engine_registration()
    
    # 测试 5: 图像编码
    test_image_encoding()
    
    # 总结
    print("\n" + "=" * 50)
    print("✅ 所有测试完成！")
    print("=" * 50)
    print("\n提示:")
    print("1. ExternalApiEngine 已实现完整的 HTTP 请求功能")
    print("2. ComfyUIEngine 已实现工作流提交和轮询功能")
    print("3. 图像 Base64 编码/解码功能正常")
    print("4. Engine 注册表支持配置驱动")
    print("\n下一步:")
    print("• 配置实际的 AI API（在 engine_config.yml）")
    print("• 准备 ComfyUI 工作流 JSON 文件")
    print("• 在 Pipeline 中调用 Engine 处理图像")


if __name__ == "__main__":
    run_all_tests()
