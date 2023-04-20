from fastapi import APIRouter
from typing import Union
router = APIRouter()


@router.get('/login')
async def login():
    return {}


@router.get('/sms')
async def get_sms_code():
    return {}


@router.get("/roles")
async def get_roles(page_index: int = 0, page_count: Union[int, None] = 10):
    return {"page_index": page_index, "page_count": page_count}

