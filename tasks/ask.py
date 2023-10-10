from app import celery
from  utils  import getAccessToken,prepareContext,saverequest
import redis
import requests
import json
import uuid
import base64
import openai
from ssdb import SSDB
import  time
import  utils
first_message  = {"role": "system", "content": '你是一个小学老师，可以回答数学、语文、英语、地理等科目问题，'}

def sendCustomMsg(answer,from_user) :
    print("send  customer message .....")
    url = "https://api.weixin.qq.com/cgi-bin/message/custom/send?access_token=ACCESS_TOKEN"
    _access_token =  getAccessToken();
    url = url.replace("ACCESS_TOKEN", _access_token)
    message = {
    "touser": "",
    "msgtype": "text",
    "text": {
        "content": ""
       }
    }
    message["text"]["content"] = answer
    message["touser"] =  from_user;
    try:
        headers = {"Content-Type": "application/json charset=utf-8"}
        _data = json.dumps(message, ensure_ascii=False)
        # print(_data)
        response= requests.post(url, data=_data.encode('utf-8'), headers=headers)
        response.raise_for_status() 
        print(response.text)
    except requests.exceptions.RequestException as e:
        print(f"An error occurred while making the request: {e}")
    # print("send  customer message  completed!")
@celery.task(name='ask')
def ask(content,from_user,chatid):
   answer = ""
   try:
        openai.api_key=utils.openai_api_key
        key = f"wxuser_{from_user}"
        response_data =  openai.ChatCompletion.create(model="gpt-4-0613",\
messages=prepareContext(key,content))
        #print(response_data)
        answer = response_data['choices'][0]['message']['content']
        if  chatid  is None:
           sendCustomMsg(answer,from_user)
        else:
            send_msg_back(answer,chatid)
        saverequest(from_user,content,answer)
   except  Exception  as  e:
         print(f" Core error occurred while asking openai api: {e}")
   return answer
