from app.api import *
from tasks.ask import ask
from utils import  checkroom, getAccessToken,filter_content
import xml.etree.ElementTree as ET
import hashlib
import time
import json
 # BluePrint參數設定
import configparser
import uuid
import base64
import openai
import logging

config = configparser.ConfigParser()
config.read('config.ini')
MESSAGE_WAIT = config['msg']['MESSAGE_WAIT'] 
MESSAGE_NO_BOT = config['msg']['MESSAGE_NO_BOT'] 
MESSAGE_INVALID = config['msg']['MESSAGE_INVALID'] 
MESSAGE_TOO_REQ = config['msg']['MESSAGE_TOO_REQ'] 
MESSAGE_WELCOME = config['msg'] ['MESSAGE_WELCOME']
MESSAGE_QUOTA = config['msg']['MESSAGE_QUOTA']


def buildResponse(from_user,to_user,answer):
    syncresponse = (
          "<xml>"
          f"<ToUserName><![CDATA[{from_user}]]></ToUserName>"
          f"<FromUserName><![CDATA[{to_user}]]></FromUserName>"
          f"<CreateTime>{int(time.time())}</CreateTime>"
          f"<MsgType><![CDATA[text]]></MsgType>"
          f"<Content><![CDATA[{answer}]]></Content>"
          "</xml>")
    return syncresponse
wechat = Blueprint('wechat', __name__)
user_cache={}
@wechat.route('/wechat',methods=['GET'])
def check():
     try:
        signature = request.args.get('signature')
        timestamp = request.args.get('timestamp')
        nonce = request.args.get('nonce')
        token = 'xbb230217'  # Replace with your actual token value
        tmpArr = [token, timestamp, nonce]
        tmpArr.sort()
        tmpStr = ''.join(tmpArr).encode('utf-8')
        tmpStr = hashlib.sha1(tmpStr).hexdigest()
        if tmpStr == signature:
           return request.args.get('echostr')
        else:
          return "Invalid signature"
     except Exception as e:
          # current_app.logger.warning(e,exc_info=True)
        #return jsonify({"msg":"add fail"}
         	return "Invalid signature"
@wechat.route('/wechat',methods=['POST'])
def handle_ask():
    current_app.logger.info("handle  message....")
    getAccessToken();
    root = ET.fromstring(request.data)
    from_user = root.find('FromUserName').text
    to_user = root.find('ToUserName').text
    answer=MESSAGE_WAIT
    if  root.find('Event') is not None and root.find('Event').text =='subscribe' :
         print("new   subcribe   welcome :")
         return buildResponse(from_user,to_user,MESSAGE_WELCOME);

    if  root.find('Content') is None:
         return buildResponse(from_user,to_user,"");

     
    if from_user in user_cache and time.time() - user_cache[from_user] <30:
        return buildResponse(from_user,to_user,MESSAGE_TOO_REQ);
    user_cache[from_user] = time.time()

    content = root.find('Content').text
    if content.startswith("tt_live"):
        parts = content.split(":")

    filtered = filter_content(content);
    if  filtered:
        return buildResponse(from_user,to_user,MESSAGE_INVALID);
    
    # do something with the content, e.g. call a machine learning model to get an answer
    ask.delay(content,from_user,None)
    current_app.logger.info("submit  to openai ")
    return  buildResponse(from_user,to_user,answer);
