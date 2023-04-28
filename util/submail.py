import aiohttp
import os


app_id = '94524'
app_key = os.environ['Lizi_Submail_Key']


class SubmailUtil:

    @staticmethod
    async def send_code(mobile: str, template: str, code: str) -> None:
        url = 'https://api-v4.mysubmail.com/sms/xsend'
        data = {'appid': app_id, 'to': mobile, 'project': template, 'signature': app_key, 'vars': {'code': code}}
        async with aiohttp.ClientSession() as session:
            async with session.post(url, json=data) as response:
                return await response.json()


