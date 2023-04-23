from fastapi import FastAPI
from api import chat, user, test

app = FastAPI()
app.include_router(test.router, prefix="/test")
app.include_router(chat.router, prefix="/chat")
app.include_router(user.router, prefix="/user")


