import json

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from api import chat, user, test
from util.log import logger
from util.secret import decode_user_token
from module.api import Code
from urllib.parse import urlencode, quote
app = FastAPI()


async def set_body(request: Request, body: bytes):
    async def receive():
        return {"type": "http.request", "body": body}
    request._receive = receive


async def edit_body(request: Request, user_id: int) -> bytes:
    j_body = await request.json()
    j_body["user_id"] = user_id
    body = json.dumps(j_body).encode(encoding="UTF-8")
    await set_body(request, body)
    return body


async def user_verify(request: Request, call_next):
    api = request.url.path
    filter_api_list = [
        "/user/login",
        "/user/sms",
        "/test/"
    ]

    if api in filter_api_list:
        return await call_next(request)
    else:
        token = request.headers.get("token")
        if token is None:
            return JSONResponse(status_code=401, content={"code": Code.TOKEN_ERROR, "msg": "Token无效，请先登录！"})
        else:
            payload = decode_user_token(token)
            if payload is None:
                return JSONResponse(status_code=401, content={"code": Code.TOKEN_ERROR, "msg": "Token无效，请先登录！"})

            else:
                if request.method == "POST":
                    await edit_body(request, payload['user_id'])
                    return await call_next(request)
                elif request.method == "GET":
                    query_params = dict(request.query_params)
                    query_params["user_id"] = payload['user_id']
                    query_str = urlencode(query_params, quote_via=quote)
                    bytes_query_str = bytes(query_str, encoding="UTF-8")
                    request.scope["query_string"] = bytes_query_str
                    return await call_next(request)

# 将中间件添加到应用程序
app.middleware('http')(user_verify)

# router
app.include_router(test.router, prefix="/test")
app.include_router(chat.router, prefix="/chat")
app.include_router(user.router, prefix="/user")


