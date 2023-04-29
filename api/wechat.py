from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from util.log import logger
router = APIRouter()


@router.get("/verify")
async def verify(signature: str, timestamp: int, nonce: str, echostr: str):
    logger.info(f"{signature}")
    logger.info(f"{timestamp}")
    logger.info(f"{nonce}")
    logger.info(f"{echostr}")
    return HTMLResponse(content=echostr)
