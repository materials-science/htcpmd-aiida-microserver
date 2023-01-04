from . import config, nacos
from .api import get_api_instance
from .app import get_app_instance
from .db import get_db_instance
from .log import log
from .mq import get_mq_instance
from .redis import redis_client

INSTANCE = config.INSTANCE
GLOBAL_CONFIG = config.GLOBAL_CONFIG
app = get_app_instance()
api = get_api_instance()
db = get_db_instance()
mq = get_mq_instance()

__all__ = (INSTANCE, GLOBAL_CONFIG, app, api, db, mq, nacos, redis_client, log)
