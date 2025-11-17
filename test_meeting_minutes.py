import requests
import json
import time

# 测试上传背景知识
def test_upload_background():
    url = "http://localhost:5001/rag/upload_background"
    files = {
        'file': open('./test_background.txt', 'rb')
    }
    response = requests.post(url, files=files)
    print("Upload background response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

# 测试生成会议记录
def test_generate_minutes(background_id=None):
    url = "http://localhost:5001/rag/generate_minutes"
    files = {
        'audio': open('./test_audio.wav', 'rb')
    }
    data = {
        'background_id': background_id
    }
    response = requests.post(url, files=files, data=data)
    print("Generate minutes response:")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

# 测试查询会议记录任务状态
def test_get_meeting_task_status(task_id):
    url = f"http://localhost:5001/rag/meeting_task/{task_id}"
    response = requests.get(url)
    print(f"Task status response ({task_id}):")
    print(json.dumps(response.json(), indent=2, ensure_ascii=False))
    return response.json()

if __name__ == "__main__":
    # 首先上传背景知识
    background_response = test_upload_background()
    background_id = background_response.get('background_id')
    
    # 然后生成会议记录
    if background_id:
        generate_response = test_generate_minutes(background_id)
    else:
        generate_response = test_generate_minutes()
    
    # 查询任务状态
    task_id = generate_response.get('task_id')
    if task_id:
        print("\n--- 查询任务状态 ---")
        # 轮询查询任务状态，直到任务完成
        for i in range(10):
            task_status = test_get_meeting_task_status(task_id)
            status = task_status.get('status')
            if status in ['completed', 'failed']:
                break
            time.sleep(5)  # 每5秒查询一次