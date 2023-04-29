from fastapi import APIRouter
from module.api import WeChatVerify
from util.log import logger
router = APIRouter()


@router.get("/verify")
async def index(wechat_verify: WeChatVerify):
    logger.info(f"{wechat_verify}")
    return True
