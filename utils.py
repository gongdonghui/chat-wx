import xml.etree.ElementTree as ET
import hashlib
import time
import configparser
import asyncio
import redis
import requests
import json
import jieba
import jieba.posseg as pseg

# 尝试导入SSDB客户端，若失败则跳过
ssdb_available = False
try:
    from ssdb import SSDB
    ssdb_available = True
except ImportError:
    SSDB = None
    print("SSDB client not available, some functionality may be limited")
config = configparser.ConfigParser()
config.read('config.ini')
ssdb_client=None
access_token_key = config['wx']['access_token_key']
lp_access_token_key = config['lp']['access_token_key']
openai_api_key =  config['openai']['apikey'] 
redis_client = None
first_message  = {"role": "system", "content": '你是一个小学老师，可以回答数学、语文、英语、地理等科目问题，'}
# 初始化jieba
jieba.setLogLevel(20)
try:
  redis_client = redis.Redis(host=str(config['redis']['ip']), port=config['redis']['port'])
  if ssdb_available:
    ssdb_client = SSDB(str(config['ssdb']['ip']),8448)
  else:
    ssdb_client = None
except  Exception as e:
   print(f"An error occurred while init db client: {e}")

with open('keywords.txt', 'r') as f:
        keywords = [line.strip() for line in f.readlines()]

def  send_msg_back(answer,chatid):  #save  answoer  for request 
    redis_client.set(chatid, answer)

def   prepareContext(key,content):
        messages = []
        if not redis_client.exists(key):
            messages =[first_message];
        else:
            messages =  json.loads(redis_client.get(key).decode('utf-8'));
        print("prev messagee:")
        print(len(messages))
        if len(messages) >= 4:
            messages = messages[-4:]
        messages.append( {"role": "user", "content": content})
        return messages

def saverequest(from_user, ask, answer):
    try:
        timestamp = str(int(time.time()))
        key = f"wxuser_{from_user}_{timestamp}"
        data = {"ask": ask, "answer": answer,"timestamp":timestamp}
        value = json.dumps(data, ensure_ascii=False)
        if ssdb_client :
           ssdb_client.set(key,value)

        rkey = f"wxuser_{from_user}"
        messages = []
        if  redis_client.exists(rkey):
            messages =  json.loads(redis_client.get(rkey).decode('utf-8'));

        if len(messages) >= 4:
             messages = messages[-4:]
        messages.append( {"role": "user", "content": ask})
        messages.append( {"role": "assistant", "content": answer})
        _val = json.dumps(messages, ensure_ascii=False)
        redis_client.setex(rkey,  86400,  _val.encode('utf-8'))
    except Exception as e:
          print(f"SSDB set error: {e}")
def  getAccessToken(backend="subcribe"):
    appid = config['api']['appid']
    appsec = config['api']['secret']
    base_url = 'https://api.weixin.qq.com/cgi-bin/token?grant_type=client_credential&appid={}&secret={}'
    token_key=access_token_key
    if  backend == 'lp':
       token_key=lp_access_token_key
       appid =  config['lp']['appid']
       appsec=  config['lp']['secret']

    access_token_val =""
    if not redis_client.exists(token_key):
       url = base_url.format(appid, appsec)
       response = requests.get(url)
       if response.status_code == 200:
         data = json.loads(response.text)
         access_token_val = data['access_token']
         redis_client.setex(token_key, 7200,access_token_val )
    else:
        value =  redis_client.get(token_key);
        access_token_val= value.decode('utf-8')
    print("get token:"+access_token_val) 
    return  access_token_val

def buildJsonResponse(from_user, to_user, chatid):
    response = {
        "ToUserName": from_user,
        "FromUserName": to_user,
        "CreateTime": int(time.time()),
        "MsgType": "text",
        "ChatId": chatid
    }
    return json.dumps(response, ensure_ascii=False).encode('utf8')
def filter_content(content):
    for keyword in keywords:
        if keyword in content:
            # Do something, for example, send an alert
            print(f"Alert: Content contains keyword '{keyword}'")
            return  True;
            break
    return  False;
def buildJsonResponse(from_user, to_user, chatid):
    response = {
        "ToUserName": from_user,
        "FromUserName": to_user,
        "CreateTime": int(time.time()),
        "MsgType": "text",
        "ChatId": chatid
    }
    return json.dumps(response, ensure_ascii=False).encode('utf8')
def  getlpAnswer(chatid):
   answer= ""
   if  redis_client.exists(chatid):
      answer = redis_client.get(chatid).decode('utf-8')
   return answer
def  gethistory(from_user):
    chat_history = []
    start_key = f"wxuser_{from_user}_0"
    end_key = f"wxuser_{from_user}_9"
    keys = ssdb_client.keys(start_key, end_key) 
    for key in keys:
           value = ssdb_client.get(key)
           chat_history.append(json.loads(value))
    return  chat_history
def  checkroom(uid):
      live_id = f"ttlive_{uid}"
      if not redis_client.exists(live_id):
             return  True;
      else: 
           return False;
def  addroom(uid):
    live_id = f"ttlive_{uid}"
    redis_client.set(live_id, "connected")
def removeroom(uid):
    live_id = f"ttlive_{uid}"
    redis_client.delete(live_id);

def load_synonyms_dict(file_path='keywords.txt'):
    """
    加载同义词词典
    :param file_path: 词典文件路径
    :return: 同义词词典，格式：{关键词: [同义词列表]}
    """
    synonyms_dict = {}
    
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith('#'):
                    continue
                words = line.split()
                if len(words) >= 2:
                    main_word = words[0]
                    synonyms = words[1:]
                    synonyms_dict[main_word] = synonyms
    except FileNotFoundError:
        # 如果词典文件不存在，返回空词典
        pass
    
    return synonyms_dict


def expand_query(query, synonyms_dict=None, topn=2):
    """
    查询扩展
    :param query: 原始查询
    :param synonyms_dict: 同义词词典
    :param topn: 每个关键词保留的同义词数量
    :return: 扩展后的查询
    """
    if not query:
        return query
    
    if synonyms_dict is None:
        synonyms_dict = load_synonyms_dict()
    
    # 使用jieba进行词性标注
    words = pseg.cut(query)
    
    expanded_words = []
    
    for word, pos in words:
        # 只处理名词、动词、形容词
        if pos.startswith('n') or pos.startswith('v') or pos.startswith('a'):
            expanded_words.append(word)
            
            # 添加同义词
            if word in synonyms_dict:
                expanded_words.extend(synonyms_dict[word][:topn])
        else:
            expanded_words.append(word)
    
    # 去重并保持顺序
    seen = set()
    result = []
    for word in expanded_words:
        if word not in seen:
            seen.add(word)
            result.append(word)
    
    return ' '.join(result)
    


