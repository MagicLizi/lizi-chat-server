from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, Integer, String
from sqlalchemy.ext.asyncio import async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import select, and_, update, insert
from sqlalchemy.exc import DatabaseError, ProgrammingError
import os
import time

db_path = os.environ["Lizi_Chat_DB"]
engine = create_async_engine(db_path,
                             pool_size=20,
                             max_overflow=0)

async_session = async_sessionmaker(engine, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    mobile = Column(String)
    name = Column(String)
    avatar_url = Column(String)
    create_at = Column(String)
    is_valid = Column(Integer)

    @staticmethod
    async def user_exist(mobile: str):
        async with async_session() as s:
            try:
                stmt = select(User).where(User.mobile == mobile)
                result = await s.execute(stmt)
                user = result.first()
                await s.commit()
                if user is not None:
                    return user[0].id
                else:
                    return 0
            except(DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1

    @staticmethod
    async def create_user(mobile: str):
        async with async_session() as s:
            try:
                stmt = insert(User).values(mobile=mobile, name="", avatar_url="", create_at=int(time.time()),
                                           is_valid=0)
                result = await s.execute(stmt)
                await s.commit()
                return result.lastrowid
            except(DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1

    @staticmethod
    async def edit_user(user_id: int, name: str, avatar_url: str):
        async with async_session() as s:
            try:
                stmt = update(User).values(id=user_id).values(name=name, avatar_url=avatar_url)
                await s.execute(stmt)
                await s.commit()
                return 1
            except(DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1


class SmsCode(Base):
    __tablename__ = 'sms_code'
    id = Column(Integer, primary_key=True)
    mobile = Column(String)
    code = Column(String)
    is_valid = Column(Integer)
    create_at = Column(Integer)

    @staticmethod
    async def get_sms_code(mobile: str):
        async with async_session() as s:
            try:
                stmt = select(SmsCode).where(and_(SmsCode.mobile == mobile,
                                                  SmsCode.is_valid == 1,
                                                  SmsCode.create_at > int(time.time()) - 60))
                result = await s.execute(stmt)
                await s.commit()
                cnt = len(result.fetchall())
                if cnt == 0:
                    # 没有未过期的code，需要发送
                    return 1
                else:
                    # 有未过期的code, 不需要发送
                    return 0
            except(DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1

    @staticmethod
    async def insert_sms_code(mobile: str, code: int):
        create_at = int(time.time())
        async with async_session() as s:
            try:
                s.add(SmsCode(mobile=mobile, code=code, create_at=create_at, is_valid=1))
                await s.commit()
                return 1
            except (DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1

    @staticmethod
    async def verify_sms_code(mobile: str, code: int):
        async with async_session() as s:
            try:
                stmt = update(SmsCode).where(and_(SmsCode.mobile == mobile,
                                                  SmsCode.code == code,
                                                  SmsCode.is_valid == 1,
                                                  SmsCode.create_at > int(time.time()) - 60)).values(is_valid=0)
                result = await s.execute(stmt)
                await s.commit()
                if result.rowcount == 1:
                    return 1
                else:
                    return 0
            except (DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1


class Role(Base):
    __tablename__ = 'role'
    id = Column(Integer, primary_key=True)
    title = Column(String)
    prompts = Column(String)
    is_valid = Column(Integer)
    create_at = Column(Integer)

    @staticmethod
    async def get_roles():
        async with async_session() as s:
            try:
                stmt = select(Role.id, Role.title).where(Role.is_valid == 1)
                roles = await s.execute(stmt)
                rst_list = []
                for role in roles:
                    rst_list.append({"id": role.id, "title": role.title})
                await s.commit()
                return rst_list
            except (DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1

    @staticmethod
    async def get_prompts_by_id(role_id: int):
        async with async_session() as s:
            try:
                stmt = select(Role.prompts).where(and_(Role.is_valid == 1, Role.id == role_id))
                role = await s.execute(stmt)
                await s.commit()
                result = role.first()
                if result is not None:
                    return result[0]
                else:
                    return -1
            except (DatabaseError, ProgrammingError) as e:
                await s.rollback()
            return -1


class WeChatUser(Base):
    __tablename__ = 'wechat_user'
    open_id = Column(String, primary_key=True)
    free_cnt = Column(Integer)
    subscribe_start = Column(String)
    subscribe_end = Column(String)
    is_valid = Column(Integer)
    create_at = Column(Integer)

    @staticmethod
    async def user_exist(open_id):
        async with async_session() as s:
            try:
                stmt = select(WeChatUser).where(WeChatUser.open_id == open_id)
                result = await s.execute(stmt)
                wechat_user = result.first()
                await s.commit()
                if wechat_user is not None:
                    return wechat_user[0].id
                else:
                    return 0
            except(DatabaseError, ProgrammingError) as e:
                await s.rollback()
                return -1

