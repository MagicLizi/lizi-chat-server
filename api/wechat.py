from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
router = APIRouter()


@router.get("/cmd")
async def verify_url(signature: str, timestamp: int, nonce: str, echostr: str):
    return HTMLResponse(content=echostr)


@router.post("/cmd")
async def deal_wechat_msg(request: Request):
    logger.info(request.body())

