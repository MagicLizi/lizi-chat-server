from fastapi import APIRouter

router = APIRouter()


@router.get("/")
async def index():
    return {"message": "Hello Lizi-Chat Get"}


@router.get("/t1")
async def t1():
    return {}


@router.get("/t2")
async def t2():
    return {"message": "t2"}
