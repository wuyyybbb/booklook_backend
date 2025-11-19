"""
任务系统快速测试脚本
用于验证 Task / Redis / Worker 骨架是否正常工作
"""
import time
import sys
from pathlib import Path

# 添加项目根目录到 Python 路径
sys.path.insert(0, str(Path(__file__).parent))

from app.services.tasks import get_task_service, get_task_queue
from app.schemas.task import TaskCreateRequest, EditMode


def test_redis_connection():
    """测试 Redis 连接"""
    print("\n" + "="*50)
    print("测试 1: Redis 连接")
    print("="*50)
    
    queue = get_task_queue()
    if queue.health_check():
        print("✅ Redis 连接正常")
        return True
    else:
        print("❌ Redis 连接失败，请检查 Redis 是否启动")
        return False


def test_create_task():
    """测试创建任务"""
    print("\n" + "="*50)
    print("测试 2: 创建任务")
    print("="*50)
    
    task_service = get_task_service()
    
    # 创建换头任务
    request = TaskCreateRequest(
        mode=EditMode.HEAD_SWAP,
        source_image="img_test_source",
        config={
            "reference_image": "img_test_reference",
            "quality": "high",
            "blend_strength": 0.8
        }
    )
    
    task_info = task_service.create_task(request)
    
    print(f"✅ 任务已创建")
    print(f"   - 任务ID: {task_info.task_id}")
    print(f"   - 状态: {task_info.status}")
    print(f"   - 模式: {task_info.mode}")
    print(f"   - 创建时间: {task_info.created_at}")
    
    return task_info.task_id


def test_get_task(task_id):
    """测试查询任务"""
    print("\n" + "="*50)
    print("测试 3: 查询任务")
    print("="*50)
    
    task_service = get_task_service()
    task_info = task_service.get_task(task_id)
    
    if task_info:
        print(f"✅ 查询成功")
        print(f"   - 任务ID: {task_info.task_id}")
        print(f"   - 状态: {task_info.status}")
        print(f"   - 进度: {task_info.progress}%")
        return True
    else:
        print(f"❌ 任务不存在: {task_id}")
        return False


def test_queue_stats():
    """测试队列统计"""
    print("\n" + "="*50)
    print("测试 4: 队列统计")
    print("="*50)
    
    task_service = get_task_service()
    stats = task_service.get_queue_stats()
    
    print(f"✅ 队列统计")
    print(f"   - 待处理任务: {stats['pending']}")
    print(f"   - 处理中任务: {stats['processing']}")
    print(f"   - 总任务数: {stats['total_tasks']}")
    
    return True


def test_task_list():
    """测试任务列表"""
    print("\n" + "="*50)
    print("测试 5: 任务列表")
    print("="*50)
    
    task_service = get_task_service()
    tasks = task_service.get_task_list(page=1, page_size=10)
    
    print(f"✅ 任务列表（共 {len(tasks)} 个）")
    for idx, task in enumerate(tasks, 1):
        print(f"   {idx}. {task.task_id} - {task.status} - {task.mode}")
    
    return True


def test_cancel_task(task_id):
    """测试取消任务"""
    print("\n" + "="*50)
    print("测试 6: 取消任务")
    print("="*50)
    
    task_service = get_task_service()
    success = task_service.cancel_task(task_id)
    
    if success:
        print(f"✅ 任务已取消: {task_id}")
        
        # 再次查询确认状态
        task_info = task_service.get_task(task_id)
        if task_info:
            print(f"   - 新状态: {task_info.status}")
        return True
    else:
        print(f"❌ 取消任务失败: {task_id}")
        return False


def test_worker_simulation():
    """测试 Worker 模拟（手动弹出任务）"""
    print("\n" + "="*50)
    print("测试 7: Worker 模拟")
    print("="*50)
    
    # 先创建一个任务
    task_service = get_task_service()
    request = TaskCreateRequest(
        mode=EditMode.BACKGROUND_CHANGE,
        source_image="img_test_bg_source",
        config={"background_type": "studio_white"}
    )
    
    task_info = task_service.create_task(request)
    print(f"✅ 创建测试任务: {task_info.task_id}")
    
    # 模拟 Worker 弹出任务
    queue = get_task_queue()
    popped_task_id = queue.pop_task(timeout=2)
    
    if popped_task_id:
        print(f"✅ Worker 获取到任务: {popped_task_id}")
        
        # 模拟处理过程
        print("   - 更新进度: 30%")
        task_service.update_task_progress(popped_task_id, 30, "正在处理...")
        time.sleep(0.5)
        
        print("   - 更新进度: 60%")
        task_service.update_task_progress(popped_task_id, 60, "接近完成...")
        time.sleep(0.5)
        
        # 模拟完成
        result = {
            "output_image": f"/results/{popped_task_id}_output.jpg",
            "thumbnail": f"/results/{popped_task_id}_thumb.jpg",
            "metadata": {"width": 1024, "height": 1536}
        }
        task_service.complete_task(popped_task_id, result)
        print("   - 任务完成")
        
        # 查询最终状态
        final_task = task_service.get_task(popped_task_id)
        if final_task:
            print(f"   - 最终状态: {final_task.status}")
            print(f"   - 结果图片: {final_task.result.output_image if final_task.result else 'None'}")
        
        return True
    else:
        print("❌ Worker 未能获取任务（超时）")
        return False


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀"*25)
    print("Formy 任务系统测试")
    print("🚀"*25)
    
    # 测试 1: Redis 连接
    if not test_redis_connection():
        print("\n❌ 测试终止：Redis 连接失败")
        return
    
    # 测试 2: 创建任务
    task_id = test_create_task()
    
    # 测试 3: 查询任务
    test_get_task(task_id)
    
    # 测试 4: 队列统计
    test_queue_stats()
    
    # 测试 5: 任务列表
    test_task_list()
    
    # 测试 6: 取消任务
    test_cancel_task(task_id)
    
    # 测试 7: Worker 模拟
    test_worker_simulation()
    
    # 总结
    print("\n" + "="*50)
    print("✅ 所有测试完成！")
    print("="*50)
    print("\n提示：")
    print("1. 可以启动真实 Worker：python -m app.services.tasks.worker")
    print("2. Worker 会自动消费队列中的任务")
    print("3. 使用 redis-cli 查看 Redis 数据：")
    print("   - LLEN formy:task:queue")
    print("   - KEYS formy:task:data:*")
    print("   - HGETALL formy:task:data:<task_id>")


if __name__ == "__main__":
    run_all_tests()

