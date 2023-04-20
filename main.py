from fastapi import FastAPI
from api import chat, user
from llm.openai_util import OpenAIUtil

OpenAIUtil.chat("123", "")

app = FastAPI()
app.include_router(chat.router, prefix="/chat")
app.include_router(user.router, prefix="/user")







