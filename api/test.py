from fastapi import APIRouter
router = APIRouter()


@router.get("/")
async def index():
    return {"message": "Hello Lizi-Chat Get"}

