import requests
import json
import time

# 示例1：上传背景知识并生成会议记录
def example_1():
    print("=== 示例1：上传背景知识并生成会议记录 ===")
    
    # 上传背景知识
    upload_url = "http://localhost:5001/rag/upload_background"
    files = {
        'file': open('./example_background.txt', 'rb')
    }
    upload_response = requests.post(upload_url, files=files)
    upload_data = upload_response.json()
    
    if 'background_id' in upload_data:
        background_id = upload_data['background_id']
        print(f"背景知识上传成功，ID: {background_id}")
        
        # 生成会议记录
        generate_url = "http://localhost:5001/rag/generate_minutes"
        audio_files = {
            'audio': open('./example_audio.wav', 'rb')
        }
        data = {'background_id': background_id}
        generate_response = requests.post(generate_url, files=audio_files, data=data)
        generate_data = generate_response.json()
        
        if 'task_id' in generate_data:
            task_id = generate_data['task_id']
            print(f"会议记录生成任务已启动，任务ID: {task_id}")
            
            # 查询任务状态
            return task_id
    
    return None

# 示例2：查询会议记录生成状态
def example_2(task_id):
    if not task_id:
        print("无效的任务ID")
        return
    
    print(f"\n=== 示例2：查询任务状态 (ID: {task_id}) ===")
    
    status_url = f"http://localhost:5001/rag/meeting_task/{task_id}"
    for i in range(5):
        status_response = requests.get(status_url)
        status_data = status_response.json()
        
        print(f"第{i+1}次查询：")
        print(f"状态：{status_data.get('status')}")
        print(f"消息：{status_data.get('message')}")
        
        if status_data.get('status') == 'completed':
            print("\n会议记录已生成：")
            print(status_data.get('minutes'))
            break
        elif status_data.get('status') == 'failed':
            print("生成失败")
            break
        
        time.sleep(3)
        print()

if __name__ == "__main__":
    # 运行示例1
    task_id = example_1()
    
    # 运行示例2
    if task_id:
        example_2(task_id)