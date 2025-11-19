"""
简单的测试 Worker
用于测试任务轮询功能
"""
import asyncio
import time
from app.services.tasks.queue import get_task_queue
from app.schemas.task import TaskStatus

async def simulate_processing(task_id: str, queue):
    """模拟任务处理过程"""
    
    # 1. 更新状态为 PROCESSING
    queue.update_task_status(task_id, TaskStatus.PROCESSING, progress=10)
    print(f"[{task_id}] 开始处理...")
    await asyncio.sleep(2)
    
    # 2. 模拟步骤 1
    queue.update_task_status(task_id, TaskStatus.PROCESSING, progress=30, current_step="加载图片")
    print(f"[{task_id}] 加载图片...")
    await asyncio.sleep(2)
    
    # 3. 模拟步骤 2
    queue.update_task_status(task_id, TaskStatus.PROCESSING, progress=50, current_step="AI 处理中")
    print(f"[{task_id}] AI 处理中...")
    await asyncio.sleep(3)
    
    # 4. 模拟步骤 3
    queue.update_task_status(task_id, TaskStatus.PROCESSING, progress=80, current_step="生成结果")
    print(f"[{task_id}] 生成结果...")
    await asyncio.sleep(2)
    
    # 5. 获取任务数据
    task_data = queue.get_task_data(task_id)
    if not task_data:
        print(f"[{task_id}] 任务数据不存在")
        return
    
    # 6. 获取原图数据
    original_data = task_data.get("data", {})
    source_image = original_data.get("source_image", "")
    
    # 构建结果数据（模拟使用原图作为结果）
    result = {
        "output_image": f"/uploads/source/{source_image}.jpg",  # 暂时用原图路径
        "thumbnail": f"/uploads/source/{source_image}.jpg",
        "metadata": {
            "processing_time": 9.0,
            "model_version": "1.0.0-test",
            "note": "This is a simulated result"
        }
    }
    
    # 7. 更新为完成状态（result 参数会自动保存）
    queue.update_task_status(
        task_id, 
        TaskStatus.DONE, 
        progress=100, 
        current_step="完成",
        result=result
    )
    
    print(f"[{task_id}] ✓ 任务完成!")


async def worker_loop():
    """Worker 主循环"""
    queue = get_task_queue()
    print("🚀 测试 Worker 已启动")
    print("📝 等待任务...")
    
    while True:
        try:
            # 从队列中取出任务
            task_id = queue.pop_task(timeout=1)
            
            if task_id:
                # 获取任务数据
                task_data = queue.get_task_data(task_id)
                
                if task_data:
                    original_data = task_data.get("data", {})
                    print(f"\n📦 收到新任务: {task_id}")
                    print(f"   模式: {original_data.get('mode', 'unknown')}")
                    print(f"   原图: {original_data.get('source_image', 'none')}")
                    
                    # 处理任务
                    await simulate_processing(task_id, queue)
                else:
                    print(f"⚠️  任务 {task_id} 数据不存在")
            else:
                # 没有任务，等待一会
                await asyncio.sleep(0.5)
                
        except KeyboardInterrupt:
            print("\n\n⏹️  Worker 停止")
            break
        except Exception as e:
            print(f"❌ 处理任务时出错: {e}")
            import traceback
            traceback.print_exc()
            await asyncio.sleep(1)


if __name__ == "__main__":
    print("=" * 60)
    print("  Formy 测试 Worker")
    print("  用于测试任务轮询功能")
    print("=" * 60)
    print()
    
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        print("\n👋 Bye!")

