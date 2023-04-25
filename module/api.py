from pydantic import BaseModel
from enum import IntEnum


class Code(IntEnum):
    SUCCESS = 200,
    # sms
    GET_SMS_ERROR = 10001,
    VER_SMS_CODE_ERROR = 10002,
    # db
    DB_ERROR = 50000
    # verify
    TOKEN_ERROR = 50001


class LiziBaseModel(BaseModel):
    user_id: int


class SmsRes:
    def __init__(self, cool_down):
        self.cool_down = cool_down


class SmsReq(BaseModel):
    mobile: str


class LoginReq(BaseModel):
    mobile: str
    code: str


class LoginRes:
    def __init__(self, token, is_new):
        self.token = token
        self.is_new = is_new


class EditProfileReq(LiziBaseModel):
    name: str
    avatar_url: str



