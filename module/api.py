from pydantic import BaseModel


class ChatSayReq(BaseModel):
    """
    聊天接口的请求类
    """
    role_id: str
    content: str


class ChatSayRes(BaseModel):
    """
    聊天接口的返回类
    """
    content: str


