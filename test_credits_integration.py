# -*- coding: utf-8 -*-
"""
测试算力扣减与 AI 任务集成
"""
import requests
import json
import time

BASE_URL = "http://localhost:8000/api/v1"
TEST_EMAIL = "test_credits@example.com"


def login_and_get_token():
    """登录并获取 token"""
    print("\n🔐 登录获取 token...")
    print("=" * 60)
    
    # 发送验证码
    send_response = requests.post(
        f"{BASE_URL}/auth/send-code",
        json={"email": TEST_EMAIL}
    )
    
    if send_response.status_code != 200:
        print(f"❌ 发送验证码失败: {send_response.text}")
        return None
    
    print(f"✓ 验证码已发送到 {TEST_EMAIL}")
    code = input("请输入验证码: ").strip()
    
    # 登录
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "code": code}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return None
    
    token = login_response.json().get("access_token")
    print(f"✓ 登录成功！")
    return token


def get_billing_info(token):
    """获取计费信息"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/billing/me", headers=headers)
    
    if response.status_code == 200:
        return response.json()
    return None


def display_billing_info(billing):
    """显示计费信息"""
    if not billing:
        print("❌ 无法获取计费信息")
        return
    
    print("\n💳 当前计费信息：")
    print("=" * 60)
    print(f"  套餐: {billing.get('current_plan_name', '无')} ({billing.get('current_plan_id', '无')})")
    print(f"  剩余算力: {billing.get('current_credits', 0)}")
    print(f"  每月总额: {billing.get('monthly_credits', 0)}")
    print(f"  使用百分比: {billing.get('credits_usage_percentage', 0):.1f}%")
    print(f"  累计使用: {billing.get('total_credits_used', 0)}")


def change_plan(token, plan_id):
    """切换套餐"""
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.post(
        f"{BASE_URL}/billing/change_plan",
        headers=headers,
        json={"plan_id": plan_id}
    )
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 切换到 {result['new_plan_name']} 套餐成功")
        print(f"  新算力: {result['new_credits']}")
        return True
    else:
        print(f"\n❌ 切换套餐失败: {response.text}")
        return False


def create_task(token, mode, source_image="test_image_123"):
    """创建任务"""
    headers = {"Authorization": f"Bearer {token}"}
    data = {
        "mode": mode,
        "source_image": source_image,
        "config": {
            "quality": "standard",
            "size": "medium"
        }
    }
    
    response = requests.post(
        f"{BASE_URL}/tasks",
        headers=headers,
        json=data
    )
    
    return response


def test_scenario_1_sufficient_credits(token):
    """场景 1: 算力充足，任务创建成功"""
    print("\n" + "=" * 60)
    print("场景 1: 算力充足 → 任务创建成功")
    print("=" * 60)
    
    # 切换到 PRO 套餐（12000 算力）
    change_plan(token, "pro")
    
    # 查看初始算力
    billing_before = get_billing_info(token)
    display_billing_info(billing_before)
    credits_before = billing_before.get('current_credits', 0)
    
    # 创建任务（HEAD_SWAP 标准配置 = 40 * 1.0 * 1.2 = 48 算力）
    print("\n📝 创建任务: HEAD_SWAP (标准质量, 中等尺寸)")
    response = create_task(token, "HEAD_SWAP")
    
    if response.status_code == 200:
        task = response.json()
        print(f"✅ 任务创建成功！")
        print(f"  任务ID: {task['task_id']}")
        print(f"  消耗算力: {task.get('credits_consumed', 0)}")
        
        # 查看剩余算力
        billing_after = get_billing_info(token)
        credits_after = billing_after.get('current_credits', 0)
        consumed = credits_before - credits_after
        
        print(f"\n💰 算力变化:")
        print(f"  扣除前: {credits_before}")
        print(f"  扣除后: {credits_after}")
        print(f"  实际扣除: {consumed}")
    else:
        print(f"❌ 任务创建失败: {response.text}")


def test_scenario_2_insufficient_credits(token):
    """场景 2: 算力不足，任务创建失败"""
    print("\n" + "=" * 60)
    print("场景 2: 算力不足 → 任务创建失败")
    print("=" * 60)
    
    # 切换到 STARTER 套餐（2000 算力）
    change_plan(token, "starter")
    
    # 消耗大部分算力
    billing = get_billing_info(token)
    current_credits = billing.get('current_credits', 0)
    
    # 消耗到只剩 30 算力
    headers = {"Authorization": f"Bearer {token}"}
    consume_amount = current_credits - 30
    requests.post(
        f"{BASE_URL}/billing/consume_credits?amount={consume_amount}",
        headers=headers
    )
    
    # 查看当前算力
    billing = get_billing_info(token)
    display_billing_info(billing)
    
    # 尝试创建任务（需要 48 算力，但只剩 30）
    print("\n📝 尝试创建任务: HEAD_SWAP (需要 48 算力)")
    response = create_task(token, "HEAD_SWAP")
    
    if response.status_code == 402:
        error = response.json()
        print(f"✅ 正确返回 402 错误")
        print(f"  错误类型: {error.get('detail', {}).get('error', 'N/A')}")
        print(f"  错误消息: {error.get('detail', {}).get('message', 'N/A')}")
        print(f"  需要算力: {error.get('detail', {}).get('required', 'N/A')}")
        print(f"  当前算力: {error.get('detail', {}).get('current', 'N/A')}")
        print(f"  缺少算力: {error.get('detail', {}).get('deficit', 'N/A')}")
    else:
        print(f"❌ 预期返回 402，实际返回 {response.status_code}")
        print(f"  响应: {response.text}")


def test_scenario_3_different_modes(token):
    """场景 3: 不同模式消耗不同算力"""
    print("\n" + "=" * 60)
    print("场景 3: 不同模式消耗不同算力")
    print("=" * 60)
    
    # 切换到 ULTIMATE 套餐（30000 算力）
    change_plan(token, "ultimate")
    
    billing_before = get_billing_info(token)
    credits_before = billing_before.get('current_credits', 0)
    
    modes = ["HEAD_SWAP", "BACKGROUND_CHANGE", "POSE_CHANGE"]
    expected_costs = [48, 36, 60]  # 标准配置下的算力消耗
    
    for i, mode in enumerate(modes):
        print(f"\n📝 创建任务: {mode}")
        response = create_task(token, mode)
        
        if response.status_code == 200:
            task = response.json()
            consumed = task.get('credits_consumed', 0)
            print(f"  ✓ 任务创建成功")
            print(f"  消耗算力: {consumed} (预期: {expected_costs[i]})")
        else:
            print(f"  ❌ 任务创建失败: {response.text}")
    
    # 查看总消耗
    billing_after = get_billing_info(token)
    credits_after = billing_after.get('current_credits', 0)
    total_consumed = credits_before - credits_after
    
    print(f"\n💰 总算力变化:")
    print(f"  扣除前: {credits_before}")
    print(f"  扣除后: {credits_after}")
    print(f"  总共扣除: {total_consumed}")
    print(f"  预期扣除: {sum(expected_costs)}")


def run_all_tests():
    """运行所有测试"""
    print("\n" + "🚀 开始测试算力扣减功能")
    print("=" * 60)
    
    # 登录
    token = login_and_get_token()
    if not token:
        print("\n❌ 登录失败，测试终止")
        return
    
    try:
        # 场景 1: 算力充足
        test_scenario_1_sufficient_credits(token)
        time.sleep(1)
        
        # 场景 2: 算力不足
        test_scenario_2_insufficient_credits(token)
        time.sleep(1)
        
        # 场景 3: 不同模式
        test_scenario_3_different_modes(token)
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    try:
        run_all_tests()
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("请确保后端正在运行: python -m uvicorn app.main:app --reload")
    except KeyboardInterrupt:
        print("\n\n⚠️ 测试被用户中断")

