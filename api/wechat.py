import asyncio

from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
import xml.etree.ElementTree as ET
import time
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


async def resp_gpt_msg(content: str, prompts: str, user_msg_id: str):
    rst = OpenAIUtil.sync_chat(content, prompts)
    message_cache[user_msg_id] = rst
    logger.info(f"用户:{user_msg_id}合法, content:{rst}")


@router.post("/cmd")
async def deal_wechat_msg(request: Request):
    valid_user = ["og8uO6YWYaAORpVxAw0fkMP7X4yY", "og8uO6cdyyIvN7s32EbSJilFirus", "og8uO6RWTp0WxLtIUWlfEsCnfMG0", "og8uO6YqqQnInYlEmu8Gs27aWA_0"]
    body = await request.body()
    root = ET.fromstring(body)
    to_user_name = root.find('./ToUserName').text
    from_user_name = root.find('./FromUserName').text
    msg_type = root.find('./MsgType').text
    if from_user_name in valid_user:
        if msg_type == "text":
            content = root.find('./Content').text
            msg_id = root.find('./MsgId').text
            user_msg_id = f"{from_user_name}_{msg_id}"
            asyncio.create_task(resp_gpt_msg(content, "", user_msg_id))
            if user_msg_id in message_cache:
                logger.info(message_cache)
                rst_content = message_cache[user_msg_id]
                return HTMLResponse(content=get_return_str(from_user_name, to_user_name, rst_content))

            # logger.info(f"用户:{from_user_name}合法, content:{content}")
            # r = await OpenAIUtil.chat(content, "")
            # logger.info(f"用户的问题结果为:{r}")

        else:
            return HTMLResponse(content=get_return_str(from_user_name, to_user_name, "你不要发除了文字以外的东西！！"))
    else:
        logger.info(f"用户:{from_user_name}非法")
        return HTMLResponse(content=get_return_str(from_user_name, to_user_name, "你是非法用户哦！！"))
