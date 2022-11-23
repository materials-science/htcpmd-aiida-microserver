# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import redis

from common.utils import DotDict
from .config import GLOBAL_CONFIG

REDIS = DotDict(GLOBAL_CONFIG.get("REDIS"))

redis_client = redis.Redis(host=REDIS.host, port=REDIS.port, db=REDIS.db,
                           username=REDIS.username, password=REDIS.password,
                           decode_responses=True)
