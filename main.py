from fastapi import FastAPI
from api import chat, user, test
from sqlalchemy import create_engine
import os
# print(os.environ["Lizi-Chat-DB"])
db_link = 'mysql://lizi:qwer1234!@rm-uf67r1uz4zcy7hya11o.mysql.rds.aliyuncs.com:3306/lizi-chat'
# engine = create_engine(db_link, echo=True)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import selectinload, sessionmaker
import os

engine = create_async_engine(
    db_link,
    pool_size=40,
    max_overflow=20
)
session_local = sessionmaker(
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    bind=engine
)


app = FastAPI()
app.include_router(test.router, prefix="/test")
app.include_router(chat.router, prefix="/chat")
app.include_router(user.router, prefix="/user")

