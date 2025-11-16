from app import celery
import requests
import os
import json
from werkzeug.utils import secure_filename
import configparser
from app.utils.storage import storage

# 加载配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 全局变量存储会议记录任务状态
meeting_tasks = {}

@celery.task(name='generate_meeting_minutes')
def generate_meeting_minutes(audio_file_path, audio_filename, background_id=None, background_content=''):
    """
    异步生成会议记录
    """
    task_id = generate_meeting_minutes.request.id
    
    # 更新任务状态
    meeting_tasks[task_id] = {
        'status': 'processing',
        'message': '正在处理音频识别...',
        'transcript': '',
        'minutes': '',
        'background_id': background_id
    }
    
    try:
        # 调用音频识别接口
        audio_recognition_url = config.get('audio', 'recognition_url', fallback='http://localhost:8001/recognize')
        
        with storage.open_file(audio_file_path, 'rb') as f:
            files = {'audio': (audio_filename, f, 'audio/wav')}
            response = requests.post(audio_recognition_url, files=files)
            response.raise_for_status()
        
        # 解析音频识别结果
        recognition_result = response.json()
        meeting_transcript = recognition_result.get('transcript', '')
        
        if not meeting_transcript:
            meeting_tasks[task_id]['status'] = 'failed'
            meeting_tasks[task_id]['message'] = '音频识别失败'
            return meeting_tasks[task_id]
        
        # 更新任务状态
        meeting_tasks[task_id]['status'] = 'processing'
        meeting_tasks[task_id]['message'] = '正在生成会议记录...'
        meeting_tasks[task_id]['transcript'] = meeting_transcript
        
        # 结合背景知识生成会议记录
        prompt = f"""
你是一位专业的会议记录生成助手，请根据以下会议转录内容和会议背景知识，生成清晰、结构化的会议记录。

会议背景知识：
{background_content}

会议转录内容：
{meeting_transcript}

会议记录要求：
1. 包含会议主题、时间、参与人员等基本信息（如果转录内容中包含）
2. 分点列出会议主要议题和讨论内容
3. 记录决策事项和行动项
4. 语言简洁、逻辑清晰
5. 格式规范，易于阅读

会议记录：
            """
        
        # 调用大模型生成会议记录
        VLLM_SERVER_URL = config.get('vllm', 'server_url', fallback='http://localhost:8000/generate')
        response = requests.post(
            VLLM_SERVER_URL,
            json={'prompt': prompt, 'temperature': 0.7, 'max_tokens': 1024}
        )
        
        if response.status_code == 200:
            meeting_minutes = response.json().get('text', '')
        else:
            meeting_minutes = '大模型服务调用失败'
        
        # 更新任务状态
        meeting_tasks[task_id]['status'] = 'completed'
        meeting_tasks[task_id]['message'] = '会议记录生成成功'
        meeting_tasks[task_id]['minutes'] = meeting_minutes
        
        # 删除存储系统中的音频文件
        storage.delete_file(audio_file_path)
        
        return meeting_tasks[task_id]
        
    except Exception as e:
        meeting_tasks[task_id]['status'] = 'failed'
        meeting_tasks[task_id]['message'] = f'生成失败：{str(e)}'
        
        # 删除临时音频文件
        if os.path.exists(audio_file_path):
            os.unlink(audio_file_path)
        
        return meeting_tasks[task_id]