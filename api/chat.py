from typing import Union
from module.db import Role
from fastapi import APIRouter, Request
from module.api import Code, RolesRes, ChatSayReq, ChatSayRes
from util.log import logger
from llm.openai_util import OpenAIUtil
router = APIRouter()


@router.get("/roles")
async def get_roles(user_id: int):
    result = await Role.get_roles()
    if result == -1:
        return {"code": Code.DB_ERROR, "msg": "系统错误"}
    return {"code": Code.SUCCESS, "data": RolesRes(result), "msg": "成功"}


@router.post("/say")
async def chat_say(req: ChatSayReq):
    # 获取prompts
    prompts = await Role.get_prompts_by_id(req.role_id)
    if prompts == -1:
        return {"code": Code.DB_ERROR, "msg": "系统错误"}
    result = OpenAIUtil.chat(req.content, prompts)
    return {"code": Code.SUCCESS, "data": ChatSayRes(result), "msg": "reply"}
#
#
# @router.get("/history")
# async def get_chat_history(role_id: int = 0, page_index: int = 0, page_count: Union[int, None] = 20):
#     return {"role_id": role_id, "page_index": page_index, page_count: page_count}

