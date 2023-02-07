# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import json

from common.event import EventUtil
from config import log
from config import mq
from constant import MqConstant


@mq.queue(exchange_name=MqConstant.EVENT_DIRECT_EXCHANGE_NAME,
          queue_name="htcpmd.test.mq.message",
          routing_key="htcpmd.test.mq.message",
          exchange_type=MqConstant.EVENT_EXCHANGE_TYPE)
@EventUtil.pre_event_handler()
def test(data, headers, message_id, message):
    log.info("message headers: ", json.dumps(message.headers, skipkeys=True))
    log.info('message props: ', json.dumps(message.properties, skipkeys=True))
    log.info('data: ', data)
    headers.update({"resp": 2})

    mq.send({
        "data": {"resp": 2}
    }, "htcpmd.test.mq.message.callback",
        MqConstant.EVENT_DIRECT_EXCHANGE_NAME,
        headers=headers)

    return True
