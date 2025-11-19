# -*- coding: utf-8 -*-
"""
测试计费 API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"

# 测试用户邮箱
TEST_EMAIL = "test_billing@example.com"


def get_test_token():
    """
    获取测试用的 token
    注意：这需要先登录或使用已有的 token
    """
    # 方法 1: 如果你已经有 token，直接返回
    # return "your_existing_token_here"
    
    # 方法 2: 通过登录获取（需要先发送验证码）
    print("\n🔐 获取测试 token...")
    print("=" * 60)
    
    # 发送验证码
    print(f"1. 发送验证码到 {TEST_EMAIL}...")
    send_code_response = requests.post(
        f"{BASE_URL}/auth/send-code",
        json={"email": TEST_EMAIL}
    )
    
    if send_code_response.status_code != 200:
        print(f"❌ 发送验证码失败: {send_code_response.text}")
        return None
    
    print("✓ 验证码已发送（请到邮箱查收）")
    
    # 等待用户输入验证码
    code = input("请输入验证码: ").strip()
    
    # 登录
    print("2. 使用验证码登录...")
    login_response = requests.post(
        f"{BASE_URL}/auth/login",
        json={"email": TEST_EMAIL, "code": code}
    )
    
    if login_response.status_code != 200:
        print(f"❌ 登录失败: {login_response.text}")
        return None
    
    login_data = login_response.json()
    token = login_data.get("access_token")
    print(f"✓ 登录成功！Token: {token[:20]}...")
    
    return token


def test_get_billing_info(token: str):
    """测试获取计费信息"""
    print("\n" + "=" * 60)
    print("测试：GET /api/v1/billing/me - 获取计费信息")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(f"{BASE_URL}/billing/me", headers=headers)
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n计费信息：")
        print(f"  用户ID: {data['user_id']}")
        print(f"  邮箱: {data['email']}")
        print(f"  当前套餐: {data['current_plan_name']} ({data['current_plan_id']})")
        print(f"  剩余算力: {data['current_credits']}")
        print(f"  每月总额: {data['monthly_credits']}")
        print(f"  累计使用: {data['total_credits_used']}")
        print(f"  使用百分比: {data['credits_usage_percentage']}%")
        print(f"  下次续费: {data['plan_renew_at']}")
    else:
        print(f"错误: {response.text}")
    
    return response.json() if response.status_code == 200 else None


def test_change_plan(token: str, plan_id: str):
    """测试切换套餐"""
    print("\n" + "=" * 60)
    print(f"测试：POST /api/v1/billing/change_plan - 切换到 {plan_id}")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    data = {"plan_id": plan_id}
    
    response = requests.post(
        f"{BASE_URL}/billing/change_plan",
        headers=headers,
        json=data
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print("\n切换结果：")
        print(f"  成功: {result['success']}")
        print(f"  消息: {result['message']}")
        print(f"  新套餐: {result['new_plan_name']} ({result['new_plan_id']})")
        print(f"  新算力: {result['new_credits']}")
        print(f"  续费时间: {result['plan_renew_at']}")
    else:
        print(f"错误: {response.text}")


def test_consume_credits(token: str, amount: int):
    """测试消耗算力"""
    print("\n" + "=" * 60)
    print(f"测试：POST /api/v1/billing/consume_credits - 消耗 {amount} 算力")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/consume_credits?amount={amount}",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 消耗成功")
        print(f"  剩余算力: {result['remaining_credits']}")
    else:
        print(f"错误: {response.text}")


def test_add_credits(token: str, amount: int):
    """测试增加算力"""
    print("\n" + "=" * 60)
    print(f"测试：POST /api/v1/billing/add_credits - 增加 {amount} 算力")
    print("=" * 60)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    response = requests.post(
        f"{BASE_URL}/billing/add_credits?amount={amount}",
        headers=headers
    )
    
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ 增加成功")
        print(f"  当前总算力: {result['total_credits']}")
    else:
        print(f"错误: {response.text}")


def run_complete_test():
    """运行完整测试流程"""
    print("\n" + "🚀 开始测试计费 API")
    print("=" * 60)
    
    # 1. 获取 token
    token = get_test_token()
    if not token:
        print("\n❌ 无法获取 token，测试终止")
        return
    
    # 2. 查看初始计费信息
    print("\n📊 查看初始状态")
    test_get_billing_info(token)
    
    # 3. 切换到 STARTER 套餐
    print("\n📦 切换套餐测试")
    test_change_plan(token, "starter")
    test_get_billing_info(token)
    
    # 4. 切换到 PRO 套餐
    test_change_plan(token, "pro")
    test_get_billing_info(token)
    
    # 5. 消耗算力测试
    print("\n💸 算力消耗测试")
    test_consume_credits(token, 100)
    test_get_billing_info(token)
    
    # 6. 增加算力测试
    print("\n💰 算力充值测试")
    test_add_credits(token, 500)
    test_get_billing_info(token)
    
    # 7. 切换到 ULTIMATE 套餐
    print("\n🎯 切换到旗舰套餐")
    test_change_plan(token, "ultimate")
    test_get_billing_info(token)
    
    print("\n" + "=" * 60)
    print("✅ 所有测试完成！")
    print("=" * 60)


if __name__ == "__main__":
    try:
        run_complete_test()
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("请确保后端正在运行: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()

