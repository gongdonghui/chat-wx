#coding:utf-8
from TikTokLive import TikTokLiveClient
from TikTokLive.types.events import CommentEvent, ConnectEvent
from app import celery

from TikTokLive.types.events import GiftEvent,LikeEvent,DisconnectEvent
import requests
import json
import configparser
import uuid
import time
import os
from ssdb import SSDB
import requests
import hashlib
import base64
import  random
from  utils  import  addroom,removeroom,getAccessToken
DY_GAME_GIFT_DEFAULT="dy001"
DY_COMMENT_MSG="live_comment";
DY_LIKE_MSG ="live_like";
DY_GIFT_MSG="live_gift";
from app import celery
from app import celery


#GAMEBACKEND_SECRET = os.getenv("GAMEBACKEND_SECRET")
#GAMEBACKEND_URL =""   #http 回调
try:
  ssdb_client = SSDB('localhost', 8448)
  print("coonected   to ssdb")
except  Exception as e:
   print(f"An error occurred while init  ssdb client: {e}")
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
_gift_config = configparser.ConfigParser()
_gift_config.read('/root/webcast/config.ini')
GAMEBACKEND_URL =_gift_config['server']['callback']
def serializeEvent(room_id, message):
    timestamp = str(int(time.time()))
    key = f"ttmsg_{room_id}_{timestamp}"
    data = {"msg": message,"timestamp":timestamp}
    value = json.dumps(data, ensure_ascii=False)
    ssdb_client.set(key,value)

def   selectgiftbywx(raw_gift) :

    if _gift_config.has_option('dy', raw_gift):
       dycode =  _gift_config['dy'][raw_gift]
       return dycode
    else:
       return  DY_GAME_GIFT_DEFAULT
def  selectrandomgift():
    values = list(_gift_config['dy'].values())
    random_value = random.choice(values)
    #print('random gift: '+random_value)  
    return random_value
def  transform_cmd(content):
    ret =''
    if content =='Trắng'  or  content == 'trắng' or   content =="trang" or  content  == "Trang":
        ret="白"
    elif  content =="Đen"   or  content =="đen"  or  content  =="den"  or   content  == "Den" :
        ret ="黑"
    elif content == 'Đổi' or  content  =="Doi" or   content=="doi"   or  content =="đổi"  or  content  =="dôi"  or  content =="Dôi":
        ret="换"
    elif content =='Trái'    or  content =="trái"  or content  =="Trai"  or  content =="trai":
        ret ="左"
    elif content  == 'Phải'   or  content =="phải" or content =="phai"  or  content =="Phai":
        ret  ="右"
    elif  content =='Giữa' or   content=="giữa"  or  content=="giua"  or  content=="Giua":
        ret  ="中"
    return ret;
def send_message(room_id, msg_type, body):
    nonce_str = "123#@!"
    timestamp = int(time.time() * 1000)  # Convert to milliseconds
    content_type = "application/json"

    headers = {
        # "x-nonce-str": nonce_str,
        # "x-timestamp": str(timestamp),
        "x-roomid": room_id,

        "x-msg-type": msg_type,
        "Content-Type": content_type
    }

    # Generate the signature
    # sig = signature(headers, body, GAMEBACKEND_SECRET)
    # headers["x-signature"] = sig
    json_string = json.dumps(body, ensure_ascii=False)
    encoded_string = json_string.encode('utf-8')
    print("call  game   server  body...")
    print(encoded_string)
    print("call   game  sever ...")

    response = requests.post(GAMEBACKEND_URL, headers=headers, data=encoded_string)

    if response.status_code == 200:
        print("Message sent successfully.")
    else:
        print("Error:", response.json()["error"])
def common_msg( event ) :
    ret  ={
        "nickname": event.user.nickname,
        "avatar_url":  event.user.avatar.urls[0],
        "sec_openid": event.user.sec_uid,
        "msg_id": str(uuid.uuid4()),
        "timestamp": int(time.time() * 1000), }
    return ret

@celery.task(name='webcast')
def startlive(room_id,uid,from_user):
  __GAME_ROOM_ID= room_id
  __LIVE_UID= uid

  async def on_comment(event: CommentEvent):
    cmd  =  transform_cmd(event.comment)
    msg= common_msg(event)
    if  len(cmd) > 0:
       msg['content'] =  cmd
       send_message(__GAME_ROOM_ID, DY_COMMENT_MSG, msg)
    else:
        msg['cotent']   =  event.comment;
    serializeEvent(__GAME_ROOM_ID,msg);
    print(f"text:::{event.user.nickname} -> {event.comment}")


  async def on_like(event: LikeEvent):
    msg = common_msg(event)
    msg['like_num'] = event.likes;
    send_message(__GAME_ROOM_ID, DY_LIKE_MSG, msg)
    serializeEvent(__GAME_ROOM_ID,msg)
    print(f"like;;;@{event.user.unique_id} liked the stream!")


  async def on_gift(event: GiftEvent):
    # Streakable gift & streak is over
    if event.gift.streakable and not event.gift.streaking:
        msg= common_msg(event)
        msg['gift_num'] = event.gift.count;
        msg['sec_gift_id'] =    selectgiftbywx(event.gift.info.name) 
        msg['gift_value']   =event.gift.info.diamond_count;
        send_message(__GAME_ROOM_ID, DY_GIFT_MSG, msg)

        serializeEvent(__GAME_ROOM_ID,msg)
        print(f"gift;;;{event.user.unique_id} sent {event.gift.count}x \"{event.gift.info.name}\"")

    # Non-streakable gift
    elif not event.gift.streakable:
        msg= common_msg(event)
        msg['gift_num'] = event.gift.count;
        msg['sec_gift_id'] =    selectgiftbywx(event.gift.info.name) 
        msg['gift_value']   =event.gift.info.diamond_count;
        send_message(__GAME_ROOM_ID, DY_GIFT_MSG, msg)
        serializeEvent(__GAME_ROOM_ID,msg)
        print(f"gift:::{event.user.unique_id} sent \"{event.gift.info.name}\"")

  async def on_connect(_: ConnectEvent):


    print("Connected to Room ID:", client.room_id)
    addroom(client.unique_id)
    sendCustomMsg("Connected:"+uid,from_user)



  async def on_disconnect(event: DisconnectEvent):
    print("Disconnected")
    removeroom(client.unique_id)
    sendCustomMsg("disconnect:"+uid,from_user)

  client: TikTokLiveClient = TikTokLiveClient(unique_id=uid)
  client.add_listener("comment", on_comment)
  client.add_listener("gift", on_gift)
  client.add_listener('like',on_like)
  client.add_listener('connect',on_connect)
  client.add_listener('disconnect',on_disconnect)
  try:
    client.run()
  except    Exception as  error:
    error.printStackTrace()
    print(f"An error occurred running  client : {error}")
    sendCustomMsg("An error occurred in  :"+uid,from_user)

