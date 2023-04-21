
from module.db import SmsCode, User
import os




class DataManager:

    @staticmethod
    async def get_sms_code(mobile: str):
        print("")
        #    async with async_session() as session:  # async_session is AsyncSession
        #     sql = selectinload(SmsCode).where(SmsCode.mobile == mobile)
        #     print(sql)
        #     return "123"

