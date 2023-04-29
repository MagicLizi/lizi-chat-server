from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
import xml.etree.ElementTree as ET
import time
from llm.openai_util import OpenAIUtil
router = APIRouter()


@router.get("/cmd")
async def verify_url(signature: str, timestamp: int, nonce: str, echostr: str):
    return HTMLResponse(content=echostr)


@router.post("/cmd")
async def deal_wechat_msg(request: Request):
    valid_user = ["og8uO6YWYaAORpVxAw0fkMP7X4yY"]
    body = await request.body()
    root = ET.fromstring(body)
    to_user_name = root.find('./ToUserName').text
    from_user_name = root.find('./FromUserName').text
    msg_type = root.find('./MsgType').text
    content = root.find('./Content').text
    msg_id = root.find('./MsgId').text
    if from_user_name in valid_user:
        logger.info(f"用户:{from_user_name}合法, content:{content}")
        # r = OpenAIUtil.chat(content, "")
        # logger.info(r)

        # 创建根元素
        root = ET.Element("xml")

        # 创建子元素
        to_user_name = ET.SubElement(root, "ToUserName")
        to_user_name.text = from_user_name

        from_user_name = ET.SubElement(root, "FromUserName")
        from_user_name.text = to_user_name

        current_timestamp = int(time.time())
        create_time = ET.SubElement(root, "CreateTime")
        create_time.text = f"{current_timestamp}"

        msg_type = ET.SubElement(root, "MsgType")
        msg_type.text = "text"

        content = ET.SubElement(root, "Content")
        content.text = "Lizi测试你好"

        # 将XML树转换为字符串
        xml_string = ET.tostring(root, encoding="utf-8", method="xml")

        print(xml_string)

    else:
        logger.info(f"用户:{from_user_name}非法, content:{content}")


