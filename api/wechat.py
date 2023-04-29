from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
import xml.etree.ElementTree as ET
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
        r = await OpenAIUtil.chat(content, "")
        logger.info(r)
    else:
        logger.info(f"用户:{from_user_name}非法, content:{content}")


