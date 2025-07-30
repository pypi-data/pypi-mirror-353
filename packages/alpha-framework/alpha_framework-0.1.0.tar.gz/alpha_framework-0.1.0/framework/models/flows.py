from sqlalchemy.sql import func
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.orm import declarative_base
from sqlalchemy import Column, Integer, String, Text, DateTime
from config.settings import DATABASE_USER, DATABASE_PASSWORD, DATABASE_HOST, DATABASE_PORT, DATABASE_NAME


def get_mysql_engine():
    return create_engine(
        url=f'mysql+pymysql://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}'
    )


def get_mysql_conn():
    return sessionmaker(
        bind=get_mysql_engine(),
        expire_on_commit=False
    )()


Base = declarative_base()


class Flows(Base):
    __tablename__ = "flows"

    id = Column(Integer, primary_key=True, autoincrement=True)
    req_method = Column(String(10), comment='请求方式')
    req_url = Column(String(255), comment='原始请求url', index=True)
    req_query = Column(Text, comment='原始请求url参数')
    req_body = Column(Text, comment='原始请求体')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, onupdate=func.now(), server_default=func.now(), comment='更新时间')


class Results(Base):
    __tablename__ = "statistics_result"

    id = Column(Integer, primary_key=True, autoincrement=True)
    total = Column(Integer, comment='用例总数')
    skipped = Column(Integer, comment='跳过用例数量')
    passed = Column(Integer, comment='用例通过数量')
    failed = Column(Integer, comment='用例失败数量')
    pass_rate = Column(Integer, comment='用例成功率')
    create_time = Column(DateTime, server_default=func.now(), comment='创建时间')
    update_time = Column(DateTime, onupdate=func.now(), server_default=func.now(), comment='更新时间')


if __name__ == '__main__':
    Flows.__table__.create(bind=get_mysql_engine(), checkfirst=True)
