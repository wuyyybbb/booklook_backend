"""
简单的 Worker 脚本 - 用于开发测试
模拟任务处理过程，逐步更新进度和状态
"""
import time
import asyncio
from app.services.tasks.queue import get_task_queue
from app.schemas.task import TaskStatus, EditMode

async def process_task_simple(task_id: str, task_data: dict):
    """
    模拟处理任务
    """
    queue = get_task_queue()
    
    print(f"\n{'='*60}")
    print(f"开始处理任务: {task_id}")
    print(f"模式: {task_data.get('mode')}")
    print(f"{'='*60}\n")
    
    # 获取任务数据
    full_task_data = queue.get_task_data(task_id)
    if not full_task_data:
        print(f"❌ 任务不存在: {task_id}")
        return
    
    try:
        # 更新任务状态为 PROCESSING
        queue.update_task_status(task_id, TaskStatus.PROCESSING.value)
        print(f"✅ 状态更新: PROCESSING")
        
        # 模拟处理步骤
        steps = [
            (10, "正在加载图片..."),
            (25, "正在分析图像特征..."),
            (40, "正在进行 AI 处理..."),
            (60, "正在优化细节..."),
            (80, "正在生成结果..."),
            (95, "正在保存图片..."),
        ]
        
        for progress, step_desc in steps:
            # 更新进度
            queue.update_task_progress(task_id, progress, step_desc)
            print(f"📊 进度更新: {progress}% - {step_desc}")
            
            # 模拟处理时间
            await asyncio.sleep(2)
        
        # 模拟结果
        result = {
            "output_image": f"/results/{task_id}_result.jpg",
            "thumbnail": f"/results/{task_id}_thumb.jpg",
            "metadata": {
                "processing_time": 12.5,
                "model": "formy-v1",
                "mode": task_data.get('mode')
            }
        }
        
        # 标记任务完成
        queue.mark_task_done(task_id, result)
        print(f"\n🎉 任务完成: {task_id}")
        print(f"结果: {result}")
        print(f"{'='*60}\n")
        
    except Exception as e:
        # 标记任务失败
        error_info = {
            "code": "PROCESSING_ERROR",
            "message": str(e),
            "details": "模拟处理过程中出错"
        }
        queue.mark_task_failed(task_id, error_info)
        print(f"\n❌ 任务失败: {task_id}")
        print(f"错误: {error_info}")
        print(f"{'='*60}\n")


async def worker_loop():
    """
    Worker 主循环
    """
    queue = get_task_queue()
    print("\n🚀 Worker 已启动，等待任务...")
    print("按 Ctrl+C 停止\n")
    
    while True:
        try:
            # 从队列取出任务
            task = queue.pop_task()
            
            if task:
                task_id, task_data = task
                
                # 处理任务
                await process_task_simple(task_id, task_data)
            else:
                # 没有任务时等待
                await asyncio.sleep(1)
                
        except KeyboardInterrupt:
            print("\n⚠️  收到停止信号，Worker 正在关闭...")
            break
        except Exception as e:
            print(f"\n❌ Worker 错误: {e}")
            await asyncio.sleep(5)


if __name__ == "__main__":
    print("""
    ╔══════════════════════════════════════════════════════════╗
    ║                                                          ║
    ║              Formy Worker - 简易版本                     ║
    ║                                                          ║
    ║  此 Worker 会模拟处理任务，逐步更新进度                   ║
    ║  用于开发测试，不执行真实的 AI 处理                       ║
    ║                                                          ║
    ╚══════════════════════════════════════════════════════════╝
    """)
    
    try:
        asyncio.run(worker_loop())
    except KeyboardInterrupt:
        print("\n✅ Worker 已停止")

