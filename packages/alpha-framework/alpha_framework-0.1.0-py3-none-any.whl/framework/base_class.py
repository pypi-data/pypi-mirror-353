import pytest
from box import Box

from framework.utils.log_util import logger
from framework.db.mysql_db import MysqlDB
from framework.db.redis_db import RedisDB
from framework.exit_code import ExitCode
from framework.http_client import ResponseUtil
from framework.global_attribute import CONTEXT, CONFIG, GlobalAttribute


class BaseTestCase(object):
    context: GlobalAttribute = CONTEXT
    config: GlobalAttribute = CONFIG
    http = None
    data: Box = None
    response: ResponseUtil = None

    def request(self, app, account, *args, **kwargs):
        try:
            self.response = getattr(getattr(self.http, app), account).request(*args, app=app, **kwargs)
            return self.response
        except AttributeError as e:
            logger.error(e)
            pytest.exit(ExitCode.APP_OR_ACCOUNT_NOT_EXIST)
            return None

    def post(self, app, account, url, data=None, json=None, **kwargs):
        return getattr(getattr(self.http, app), account).post(app, url, data=data, json=json, **kwargs)

    def get(self, app, account, url, params=None, **kwargs):
        return getattr(getattr(self.http, app), account).get(app, url, params=params, **kwargs)

    def put(self, app, account, url, data=None, **kwargs):
        return getattr(getattr(self.http, app), account).put(app, url, data=data, **kwargs)

    def delete(self, app, account, url, **kwargs):
        return getattr(getattr(self.http, app), account).delete(app, url, **kwargs)

    @staticmethod
    def mysql_conn(db, app=CONTEXT.app):
        return MysqlDB(**CONFIG.get(app=app, key="mysql").get(db))

    @staticmethod
    def redis_conn(db, app=CONTEXT.app):
        return RedisDB(**CONFIG.get(app=app, key="redis"), db=db)
