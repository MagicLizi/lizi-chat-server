import asyncio
from fastapi import APIRouter, Request
from fastapi.responses import HTMLResponse
from util.log import logger
import xml.etree.ElementTree as ET
import time
import tiktoken
import aiohttp
from urllib.parse import urlencode
import os
from llm.openai_util import OpenAIUtil
import json
from wechatpayv3 import SignType, WeChatPay, WeChatPayType

router = APIRouter()


def get_return_str(from_user_name: str, to_user_name: str, content: str):
    # 创建根元素
    root = ET.Element("xml")
    # 创建子元素
    to_user_name_xml = ET.SubElement(root, "ToUserName")
    to_user_name_xml.text = from_user_name
    from_user_name_xml = ET.SubElement(root, "FromUserName")
    from_user_name_xml.text = to_user_name
    current_timestamp = int(time.time())
    create_time = ET.SubElement(root, "CreateTime")
    create_time.text = f"{current_timestamp}"
    msg_type = ET.SubElement(root, "MsgType")
    msg_type.text = "text"

    content_xml = ET.SubElement(root, "Content")
    content_xml.text = content
    # 将XML树转换为字符串
    xml_string = ET.tostring(root, encoding="utf-8", method="xml")
    return xml_string


@router.get("/cmd")
async def verify_url(signature: str, timestamp: int, nonce: str, echostr: str):
    return HTMLResponse(content=echostr)


message_cache = {}
message_cache_try_cnt = {}
user_chat_history = {}
token_dic = {
    "value": "",
    "expires": 0
}


async def resp_gpt_msg(content: str, prompts: str, user_msg_id: str, user_id: str, token, from_user_name):
    if user_id not in user_chat_history:
        user_chat_history[user_id] = list()

    # 计算token数量
    cur_length = 0
    enc = tiktoken.get_encoding("cl100k_base")
    for msg in user_chat_history[user_id]:
        enc_rst = enc.encode(msg['content'])
        rst_length = len(enc_rst)
        cur_length = cur_length + rst_length

    logger.info(f"{user_id} 当前聊天记录Token长度:{cur_length}")

    if cur_length >= 3500:
        logger.info(f"{user_id} 需要清空聊天记录，已经大于3500了")
        user_chat_history[user_id] = list()

    rst = await OpenAIUtil.chat(content=content, prompts=prompts, chat_history=user_chat_history[user_id])
    logger.info(f"{user_msg_id} 返回:{rst}")
    message_cache[user_msg_id] = rst

    # 保存用户聊天记录
    user_chat_history[user_id].append({"role": "user", "content": content})
    user_chat_history[user_id].append({"role": "assistant", "content": rst})

    await send_custom_msg(token, from_user_name, rst)


async def send_custom_msg(token, open_id, msg):
    params = {'access_token': token}
    url = f"https://api.weixin.qq.com/cgi-bin/message/custom/send?{urlencode(params)}"
    data = {
        "touser": open_id,
        "msgtype": "text",
        "text":
            {
                "content": msg
            }
    }
    json_data = json.dumps(data, ensure_ascii=False)
    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=json_data) as response:
            return await response.json()


async def get_user_info(token, openid):
    params = {'access_token': token,
              'openid': openid}
    url = f"https://api.weixin.qq.com/cgi-bin/user/info?{urlencode(params)}"
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as response:
            res = await response.json()
            return res


async def get_access_token():
    need_new = False
    e_time = token_dic['expires']
    c_time = int(time.time())

    if c_time - 100 > e_time:
        need_new = True

    if need_new:
        app_id = os.environ['WX_APPID']
        app_key = os.environ['WX_APP_SECRECT']
        params = {'grant_type': 'client_credential',
                  'appid': app_id,
                  'secret': app_key}
        url = f'https://api.weixin.qq.com/cgi-bin/token?{urlencode(params)}'
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                res = await response.json()
                if 'access_token' in res:
                    token_dic["value"] = res['access_token']
                    token_dic["expires"] = int(time.time()) + res['expires_in']
                    return token_dic["value"]
                else:
                    return -1
    else:
        return token_dic["value"]


@router.post("/cmd")
async def deal_wechat_msg(request: Request):
    # 先不需要数据库
    valid_user = ["ocZ6M5sE2AdKmvzd40GQ2fyKVZMU",
                  "ocZ6M5hxSsxITkCJyFUUBgUyUDLY",
                  "ocZ6M5lx03t2yDX4Q8r1Upks9UvQ",
                  "ocZ6M5gj0vyKt6C6ZzEeSr5viq0g"]
    body = await request.body()
    root = ET.fromstring(body)
    to_user_name = root.find('./ToUserName').text
    from_user_name = root.find('./FromUserName').text
    msg_type = root.find('./MsgType').text
    if from_user_name in valid_user:
        token = await get_access_token()
        if token != -1:
            if msg_type == "text":
                content = root.find('./Content').text
                msg_id = root.find('./MsgId').text
                user_msg_id = f"{from_user_name}_{msg_id}"
                asyncio.create_task(resp_gpt_msg(content, "", user_msg_id, from_user_name, token, from_user_name))
                return HTMLResponse(content=get_return_str(from_user_name, to_user_name, f"思考中...请耐心等待..."
                                                                                         f" http://aichat.magiclizi.com"
                                                                                         f"/wechat/pay?open_id={from_user_name}"))
            else:
                return HTMLResponse(
                    content=get_return_str(from_user_name, to_user_name, "你不要发除了文字以外的东西！！"))
        else:
            return HTMLResponse(
                content=get_return_str(from_user_name, to_user_name, "系统错误！！"))

    else:
        logger.info(f"用户:{from_user_name}非法")
        return HTMLResponse(
            content=get_return_str(from_user_name, to_user_name, "你是非法用户哦！！找Lizi！！如果你不认识她，就算了！"))


async def wechat_pre_order(open_id):
    current_dir = os.getcwd()
    file_path = os.path.join(current_dir, 'cert/apiclient_key.pem')
    with open(file_path) as f:
        private_key = f.read()
        print(private_key)

    serial_id = "4AE288AFED34296BEF1394917537DA9B34B3B788"
    api_v3_key = "emha49esGph4CJcYQhHxFEYYwdr7paBg"
    app_id = "wxe0768b96f150e55a"
    mch_id = "1643876096"

    # 初始化
    wxpay = WeChatPay(
        wechatpay_type=WeChatPayType.JSAPI,
        mchid=mch_id,
        private_key=private_key,
        cert_serial_no=serial_id,
        apiv3_key=api_v3_key,
        appid=app_id,
        notify_url='https://www.weixin.qq.com/wxpay/pay.php',
        cert_dir=None,
        logger=logger,
        partner_mode=False,
        proxy=None)

    out_trade_no = '1217752501201407033233368318'
    description = '测试商品'
    amount = 1
    code, message = wxpay.pay(
        description=description,
        out_trade_no=out_trade_no,
        amount={'total': amount},
        pay_type=WeChatPayType.JSAPI
    )
    print(code)
    print(message)


@router.get("/pay")
async def try_pay(request: Request):
    rst = await wechat_pre_order(request.query_params["open_id"])
    print(rst)
    return HTMLResponse(content="""
    <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <title>微信支付</title>
            <script src="https://res.wx.qq.com/open/js/jweixin-1.6.0.js"></script>
            <script>
                // 微信 JSAPI 配置
                wx.config({
                    debug: false,
                    appId: '微信公众号 APPID',
                    timestamp: '生成签名的时间戳',
                    nonceStr: '生成签名的随机字符串',
                    signature: '生成的签名',
                    jsApiList: ['chooseWXPay']
                });
                
                // 点击支付按钮
                function pay() {
                    // 调用微信支付接口
                    wx.chooseWXPay({
                        timestamp: '生成预支付订单的时间戳',
                        nonceStr: '生成预支付订单的随机字符串',
                        package: '预支付订单信息',
                        signType: 'MD5',
                        paySign: '生成的支付签名',
                        success: function (res) {
                            // 支付成功后的回调函数
                            alert('支付成功');
                        },
                        fail: function (res) {
                            // 支付失败后的回调函数
                            alert('支付失败');
                        }
                    });
                }
                window.onload = function() {
                    alert("123")
                    pay();
                };
            </script>
        </head>
        <body>
            <button onclick="pay()">微信支付</button>
        </body>
        </html>
    """)
