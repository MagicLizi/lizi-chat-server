from fastapi import APIRouter
from typing import Union
from module.db import SmsCode,User
from module.api import SmsReq, SmsRes, Code, LoginReq, LoginRes, EditProfileReq
from util.submail import SubmailUtil
import random
from util.secret import generate_user_token
router = APIRouter()


@router.post('/login')
async def login(login_req: LoginReq):
    # 先校验验证码是否正确
    ms_verify_rst = await SmsCode.verify_sms_code(login_req.mobile, login_req.code)
    if ms_verify_rst == 1:
        user_id = await User.user_exist(login_req.mobile)
        if user_id > 0:
            # 账号存在直接登录
            token = generate_user_token(user_id, login_req.mobile)
            return {"code": Code.SUCCESS, "data": LoginRes(token=token, is_new=False), "msg": "登录成功"}
        else:
            # 账号不存在就自动注册
            user_id = await User.create_user(login_req.mobile)
            if user_id > 0:
                token = generate_user_token(user_id, login_req.mobile)
                return {"code": Code.SUCCESS, "data": LoginRes(token=token, is_new=True),
                        "msg": "注册成功"}
            else:
                return {"code": Code.DB_ERROR, "msg": "系统错误"}
    elif ms_verify_rst == 0:
        return {"code": Code.VER_SMS_CODE_ERROR, "msg": "验证码错误"}
    elif ms_verify_rst == -1:
        return {"code": Code.DB_ERROR, "msg": "系统错误"}


@router.post('/sms')
async def get_sms_code(sms_req: SmsReq):
    get_sms_rst = await SmsCode.get_sms_code(sms_req.mobile)
    if get_sms_rst == 1:
        # 生成验证码，并且插入数据库
        digits = "0123456789"
        code = ""
        for i in range(6):
            index = random.randint(0, len(digits) - 1)
            code += digits[index]
        insert_rst = await SmsCode.insert_sms_code(sms_req.mobile, code)
        if insert_rst != -1:
            # 发送验证码
            send_rst = await SubmailUtil.send_code(sms_req.mobile, "4O5BL2", code)
            if send_rst["status"] == "success":
                return {"code": Code.SUCCESS, "data": SmsRes(60), "msg": "获取验证码成功"}
            else:
                return {"code": Code.GET_SMS_ERROR, "msg": "发送验证码失败"}
        else:
            return {"code": Code.DB_ERROR, "msg": "系统错误"}
    elif get_sms_rst == 0:
        return {"code": Code.GET_SMS_ERROR, "msg": "发送验证码过于频繁"}
    elif get_sms_rst == -1:
        return {"code": Code.DB_ERROR, "msg": "系统错误"}


@router.post("/edit_profile")
async def edit_user_profile(edit_req: EditProfileReq):
    result = await User.edit_user(edit_req.user_id, edit_req.name, edit_req.avatar_url)
    if result == 1:
        return {"code": Code.SUCCESS, "msg": "设置成功"}
    else:
        return {"code": Code.DB_ERROR, "msg": "系统错误"}
