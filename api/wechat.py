import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
import xml.etree.ElementTree as ET
import time
import tiktoken
import re
from llm.openai_util import OpenAIUtil

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


async def resp_gpt_msg(content: str, prompts: str, user_msg_id: str, user_id: str):

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


@router.post("/cmd")
async def deal_wechat_msg(request: Request):
    # 先不需要数据库
    valid_user = ["og8uO6YWYaAORpVxAw0fkMP7X4yY",
                  "og8uO6cdyyIvN7s32EbSJilFirus",
                  "og8uO6RWTp0WxLtIUWlfEsCnfMG0",
                  "og8uO6YqqQnInYlEmu8Gs27aWA_0",
                  "og8uO6eM7aKgmcMqqBdlhCzxAybk",
                  "og8uO6ZfDYWQ4T82p0DPhIVZMJNk",
                  "og8uO6dMCU-q3JgitiXUKMNnWWq0"]
    body = await request.body()
    root = ET.fromstring(body)
    to_user_name = root.find('./ToUserName').text
    from_user_name = root.find('./FromUserName').text
    msg_type = root.find('./MsgType').text
    if from_user_name in valid_user:
        if msg_type == "text":
            content = root.find('./Content').text
            msg_id = root.find('./MsgId').text

            # 判断msg_id 是不是重试
            user_msg_id = f"{from_user_name}_{msg_id}"

            # 先判断是不是缓存命令
            pattern = r'msg_id:(\w+)'
            match = re.search(pattern, content)
            if match:
                tmp_user_msg_id = match.group(1)
                if tmp_user_msg_id in message_cache:
                    rst = message_cache[tmp_user_msg_id]
                    del message_cache[tmp_user_msg_id]
                    del message_cache_try_cnt[tmp_user_msg_id]
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst))
                else:
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, f"{tmp_user_msg_id} 不存在，或者GPT还在应答中，可以等30s在尝试"))

            if user_msg_id not in message_cache_try_cnt:
                message_cache_try_cnt[user_msg_id] = 1

            else:
                message_cache_try_cnt[user_msg_id] = message_cache_try_cnt[user_msg_id] + 1

            cur_try_cnt = message_cache_try_cnt[user_msg_id]
            logger.info(f'{user_msg_id} 当前尝试次数:{cur_try_cnt}')
            if cur_try_cnt == 1:
                # 只有第一次需要发送请求,4s内有返回则返回，没有则等待重试
                asyncio.create_task(resp_gpt_msg(content, "", user_msg_id, from_user_name))
                await asyncio.sleep(4.5)
                if user_msg_id in message_cache:
                    rst = message_cache[user_msg_id]
                    del message_cache[user_msg_id]
                    del message_cache_try_cnt[user_msg_id]
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst))
                else:
                    await asyncio.sleep(20)
            elif cur_try_cnt == 2:
                # 第二次只需要获取就行
                if user_msg_id in message_cache:
                    rst = message_cache[user_msg_id]
                    del message_cache[user_msg_id]
                    del message_cache_try_cnt[user_msg_id]
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst))
                await asyncio.sleep(4.5)
                # 4.5后再尝试获取一次
                if user_msg_id in message_cache:
                    rst = message_cache[user_msg_id]
                    del message_cache[user_msg_id]
                    del message_cache_try_cnt[user_msg_id]
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst))
                else:
                    await asyncio.sleep(20)
            elif cur_try_cnt == 3:
                if user_msg_id in message_cache:
                    rst = message_cache[user_msg_id]
                    del message_cache[user_msg_id]
                    del message_cache_try_cnt[user_msg_id]
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst))
                await asyncio.sleep(4.5)
                # 4.5后再尝试获取一次，如果没有则返回报错
                if user_msg_id in message_cache:
                    rst = message_cache[user_msg_id]
                    del message_cache[user_msg_id]
                    del message_cache_try_cnt[user_msg_id]
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst))
                else:
                    return HTMLResponse(content=get_return_str(from_user_name, to_user_name, f"GPT"
                                                                                             f"超时-你可以尝试直接发送后面括号中的内容("
                                                                                             f"不包括括号)查询结果（最好等个30s-1"
                                                                                             f"分钟） (msg_id:"
                                                                                             f"{user_msg_id})"))

        else:
            return HTMLResponse(content=get_return_str(from_user_name, to_user_name, "你不要发除了文字以外的东西！！"))
    else:
        logger.info(f"用户:{from_user_name}非法")
        return HTMLResponse(content=get_return_str(from_user_name, to_user_name, "你是非法用户哦！！找Lizi！！如果你不认识她，就算了！"))
