import requests
import json

# 服务器地址
BASE_URL = "http://localhost:5001"

def test_upload_text():
    """测试上传文本接口"""
    print("测试上传文本接口...")
    url = f"{BASE_URL}/rag/upload"
    
    # 测试文本
    test_text = """
    这是第一段测试文本。它包含了一些句子，用于测试文本分块功能。
    
    这是第二段测试文本。它与第一段之间有一个空行，用于测试按段分割。
    
    这是第三段测试文本，内容比较长。它包含了更多的句子，以便测试固定长度分块和滑动窗口功能。文本分块是RAG系统中的重要组成部分，它将长文本分割成适合处理的小块，同时保持上下文的连贯性。滑动窗口技术可以确保相邻块之间有一定的重叠，从而避免信息丢失。
    """
    
    # 测试1：默认固定长度分块
    data = {
        "text": test_text
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"  默认固定长度分块 - 状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")
    
    # 测试2：按段分割
    data = {
        "text": test_text,
        "mode": "paragraph"
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"  按段分割 - 状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")
    
    # 测试3：自定义块大小和滑动窗口
    data = {
        "text": test_text,
        "chunk_size": 200,
        "chunk_overlap": 50
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"  自定义块大小和滑动窗口 - 状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  结果: {result}")
    except Exception as e:
        print(f"  错误: {e}")

def test_query():
    """测试查询接口"""
    print("测试查询接口...")
    url = f"{BASE_URL}/rag/query"
    
    data = {
        "query": "什么是RAG系统中的文本分块？"
    }
    
    try:
        response = requests.post(url, data=data)
        print(f"  状态码: {response.status_code}")
        if response.status_code == 200:
            result = response.json()
            print(f"  问题: {result.get('query', '')}")
            print(f"  回答: {result.get('answer', '')[:100]}...")
    except Exception as e:
        print(f"  错误: {e}")

if __name__ == "__main__":
    test_upload_text()
    test_query()