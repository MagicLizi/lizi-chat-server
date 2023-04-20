from module.api import ChatSayReq
from typing import Union
from fastapi import APIRouter
router = APIRouter()


@router.post("/say")
async def chat_say(req: ChatSayReq):
    return {"role_id": req.role_id, "content": req.content}


@router.get("/history")
async def get_chat_history(role_id: int = 0, page_index: int = 0, page_count: Union[int, None] = 20):
    return {"role_id": role_id, "page_index": page_index, page_count: page_count}

