# -*- coding: utf-8 -*-
"""
测试套餐配置 API
"""
import requests
import json

BASE_URL = "http://localhost:8000/api/v1"


def test_list_plans():
    """测试获取所有套餐"""
    print("\n" + "=" * 60)
    print("测试：GET /api/v1/plans - 获取所有套餐")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/plans")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"套餐总数: {data['total']}")
        print("\n套餐列表：")
        for plan in data['plans']:
            featured = " ⭐推荐" if plan['is_featured'] else ""
            print(f"\n  - {plan['name']}{featured}")
            print(f"    ID: {plan['plan_id']}")
            print(f"    价格: ¥{plan['price_month']}/月 (原价: ¥{plan['price_original']}/月)")
            print(f"    算力: {plan['monthly_credits']}")
            print(f"    图片: 约 {plan['image_count']} 张")
            print(f"    功能: {len(plan['features'])} 项")
    else:
        print(f"错误: {response.text}")


def test_get_plan_by_id(plan_id: str):
    """测试获取单个套餐"""
    print("\n" + "=" * 60)
    print(f"测试：GET /api/v1/plans/{plan_id} - 获取单个套餐")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/plans/{plan_id}")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        plan = response.json()
        print(f"\n套餐详情：")
        print(f"  名称: {plan['name']}")
        print(f"  ID: {plan['plan_id']}")
        print(f"  价格: ¥{plan['price_month']}/月")
        print(f"  原价: ¥{plan['price_original']}/月")
        print(f"  节省: ¥{plan['price_original'] - plan['price_month']}/月")
        print(f"  算力: {plan['monthly_credits']}")
        print(f"  图片: 约 {plan['image_count']} 张")
        print(f"  推荐: {'是' if plan['is_featured'] else '否'}")
        print(f"\n  功能列表:")
        for feature in plan['features']:
            print(f"    ✓ {feature}")
    else:
        print(f"错误: {response.text}")


def test_get_featured_plan():
    """测试获取推荐套餐"""
    print("\n" + "=" * 60)
    print("测试：GET /api/v1/plans/featured/current - 获取推荐套餐")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/plans/featured/current")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 200:
        plan = response.json()
        print(f"\n推荐套餐：{plan['name']} ⭐")
        print(f"  价格: ¥{plan['price_month']}/月")
        print(f"  算力: {plan['monthly_credits']}")
        print(f"  图片: 约 {plan['image_count']} 张")
    else:
        print(f"错误: {response.text}")


def test_invalid_plan_id():
    """测试不存在的套餐ID"""
    print("\n" + "=" * 60)
    print("测试：GET /api/v1/plans/invalid - 不存在的套餐")
    print("=" * 60)
    
    response = requests.get(f"{BASE_URL}/plans/invalid")
    print(f"状态码: {response.status_code}")
    
    if response.status_code == 404:
        error = response.json()
        print(f"✓ 正确返回 404: {error['detail']}")
    else:
        print(f"响应: {response.text}")


if __name__ == "__main__":
    print("\n" + "🚀 开始测试套餐配置 API")
    print("=" * 60)
    
    try:
        # 测试 1: 获取所有套餐
        test_list_plans()
        
        # 测试 2: 获取每个套餐的详情
        for plan_id in ["starter", "basic", "pro", "ultimate"]:
            test_get_plan_by_id(plan_id)
        
        # 测试 3: 获取推荐套餐
        test_get_featured_plan()
        
        # 测试 4: 测试错误情况
        test_invalid_plan_id()
        
        print("\n" + "=" * 60)
        print("✅ 所有测试完成！")
        print("=" * 60)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ 错误: 无法连接到后端服务")
        print("请确保后端正在运行: python -m uvicorn app.main:app --reload")
    except Exception as e:
        print(f"\n❌ 测试失败: {e}")

