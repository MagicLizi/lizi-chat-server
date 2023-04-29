from fastapi import APIRouter
from module.api import WeChatVerify
router = APIRouter()


@router.get("/verify")
async def index(wechat_verify: WeChatVerify):
    print(f"{wechat_verify}")
    return True
