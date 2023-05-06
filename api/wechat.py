import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
import xml.etree.ElementTree as ET
import time
import tiktoken
import aiohttp
from urllib.parse import urlencode
import os
from llm.openai_util import OpenAIUtil
import json

router = APIRouter()


def get_return_str(from_user_name: str, to_user_name: str, content: str):
    # 创建根元素
    root = ET.Element("xml")
    # 创建子元素
    to_user_name_xml = ET.SubElement(root, "ToUserName")
    to_user_name_xml.text = from_user_name
    from_user_name_xml = ET.SubElement(root, "FromUserName")
    from_user_name_xml.text = to_user_name
    current_timestamp = int(time.time())
    create_time = ET.SubElement(root, "CreateTime")
    create_time.text = f"{current_timestamp}"
    msg_type = ET.SubElement(root, "MsgType")
    msg_type.text = "text"

    content_xml = ET.SubElement(root, "Content")
    content_xml.text = content
    # 将XML树转换为字符串
    xml_string = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_string


@router.get("/cmd")
async def verify_url(signature: str, timestamp: int, nonce: str, echostr: str):
    return HTMLResponse(content=echostr)


message_cache = {}
message_cache_try_cnt = {}
user_chat_history = {}
token_dic = {
    "value": "",
    "expires": 0
}


async def resp_gpt_msg(content: str, prompts: str, user_msg_id: str, user_id: str, token, from_user_name):
    if user_id not in user_chat_history:
        user_chat_history[user_id] = list()

    # 计算token数量
    cur_length = 0
    enc = tiktoken.get_encoding("cl100k_base")
    for msg in user_chat_history[user_id]:
        enc_rst = enc.encode(msg['content'])
        rst_length = len(enc_rst)
        cur_length = cur_length + rst_length

    logger.info(f"{user_id} 当前聊天记录Token长度:{cur_length}")

    if cur_length >= 3500:
        logger.info(f"{user_id} 需要清空聊天记录，已经大于3500了")
        user_chat_history[user_id] = list()

    rst = await OpenAIUtil.chat(content=content, prompts=prompts, chat_history=user_chat_history[user_id])
    logger.info(f"{user_msg_id} 返回:{rst}")
    message_cache[user_msg_id] = rst

    # 保存用户聊天记录
    user_chat_history[user_id].append({"role": "user", "content": content})
    user_chat_history[user_id].append({"role": "assistant", "content": rst})

    await send_custom_msg(token, from_user_name, rst)


async def send_custom_msg(token, open_id, msg):
    params = {'access_token': token}
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?{urlencode(params)}"
    data = {
        "touser": open_id,
        "msgtype": "text",
        "text":
            {
                "content": msg
            }
    }
    json_data = json.dumps(data)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json_data) as response:
            return await response.json()


async def get_user_info(token, openid):
    params = {'access_token': token,
              'openid': openid}
    url = f"https://api.weixin.qq.com/cgi-bin/user/info?{urlencode(params)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            res = await response.json()
            return res


async def get_access_token():
    need_new = False
    e_time = token_dic['expires']
    c_time = int(time.time())

    if c_time - 100 > e_time:
        need_new = True

    if need_new:
        app_id = os.environ['WX_APPID']
        app_key = os.environ['WX_APP_SECRECT']
        params = {'grant_type': 'client_credential',
                  'appid': app_id,
                  'secret': app_key}
        url = f'https://api.weixin.qq.com/cgi-bin/token?{urlencode(params)}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                res = await response.json()
                if 'access_token' in res:
                    token_dic["value"] = res['access_token']
                    token_dic["expires"] = int(time.time()) + res['expires_in']
                    return token_dic["value"]
                else:
                    return -1
    else:
        return token_dic["value"]


@router.post("/cmd")
async def deal_wechat_msg(request: Request):
    # 先不需要数据库
    valid_user = ["ocZ6M5sE2AdKmvzd40GQ2fyKVZMU"]
    body = await request.body()
    root = ET.fromstring(body)
    to_user_name = root.find('./ToUserName').text
    from_user_name = root.find('./FromUserName').text
    msg_type = root.find('./MsgType').text
    if from_user_name in valid_user:
        token = await get_access_token()
        if token != -1:
            if msg_type == "text":
                content = root.find('./Content').text
                msg_id = root.find('./MsgId').text
                user_msg_id = f"{from_user_name}_{msg_id}"
                asyncio.create_task(resp_gpt_msg(content, "", user_msg_id, from_user_name, token, from_user_name))
            else:
                return HTMLResponse(
                    content=get_return_str(from_user_name, to_user_name, "你不要发除了文字以外的东西！！"))
        else:
            return HTMLResponse(
                content=get_return_str(from_user_name, to_user_name, "系统错误！！"))

    else:
        logger.info(f"用户:{from_user_name}非法")
        return HTMLResponse(
            content=get_return_str(from_user_name, to_user_name, "你是非法用户哦！！找Lizi！！如果你不认识她，就算了！"))
