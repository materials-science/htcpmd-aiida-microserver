# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
from enum import Enum


class BizJobStatusEnum(Enum):
    COMPLETED = 0
    DELETED = 1
    FAILED = 2
    RUNNING = 3
    SUBMITTING = 4
    SUBMITTED = 5
    CREATING = 6
    CREATED = 7
    WAITING = 8
    IDLE = 9
    PAUSED = 10
    SUSPEND = 11


class BizJobConstant:
    REDIS_KEY = "biz_job"
