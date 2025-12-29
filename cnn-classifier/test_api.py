# 保存为 test_api.py 并运行
import requests
import json

BASE_URL = "http://localhost:8000"

def test_all_endpoints():
    print("="*50)
    print("API端点全面测试")
    print("="*50)
    
    # 1. 测试健康检查
    print("\n1. 测试健康检查 /health")
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"   状态码: {resp.status_code}")
        print(f"   响应: {resp.json()}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 2. 测试Web界面
    print("\n2. 测试Web界面 /")
    try:
        resp = requests.get(BASE_URL)
        print(f"   状态码: {resp.status_code}")
        print(f"   响应类型: HTML ({len(resp.text)} 字符)")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 3. 测试API文档
    print("\n3. 测试API文档 /docs")
    try:
        resp = requests.get(f"{BASE_URL}/docs")
        print(f"   状态码: {resp.status_code}")
    except Exception as e:
        print(f"   失败: {e}")
    
    # 4. 上传测试图片
    print("\n4. 测试图片识别 /predict")
    print("   请准备测试图片路径，或使用以下方式创建测试:")
    print("   - 桌面放几张测试图片 (cat.jpg, car.jpg, etc.)")
    print("   - 或使用代码生成测试请求")
    
    return True

if __name__ == "__main__":
    test_all_endpoints()