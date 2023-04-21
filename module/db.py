from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String

Base = declarative_base()


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    mobile = Column(String)
    name = Column(String)
    avatar_url = Column(String)
    create_at = Column(String)
    is_valid = Column(Integer)


class SmsCode(Base):
    __tablename__ = 'sms_code'
    id = Column(Integer, primary_key=True)
    mobile = Column(String)
    code = Column(String)
    is_valid = Column(Integer)
    create_at = Column(String)

# 创建所有数据表
# Base.metadata.create_all(engine)

