# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
from flask_rabmq.utils import ExchangeType


class MqConstant:
    EVENT_EXCHANGE_TYPE = ExchangeType.DIRECT
    EVENT_DIRECT_EXCHANGE_NAME = "htcpmd.event"
    EVENT_DEFAULT_QUEUE_NAME = "htcpmd.default"
    BIZ_JOB_STATUS_UPDATE_QUEUE_NAME = "htcpmd.biz_job.status.update"
    STRUCTURE_UPLOAD_QUEUE_NAME = "htcpmd.structure.upload"
    STRUCTURE_IMPORT_QUEUE_NAME = "htcpmd.structure.import"
    STRUCTURE_UPLOAD_CALLBACK_QUEUE_NAME = "htcpmd.structure.upload.callback"
    STRUCTURE_IMPORT_CALLBACK_QUEUE_NAME = "htcpmd.structure.import.callback"
