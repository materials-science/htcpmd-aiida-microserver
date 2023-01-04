# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
from flask_rabmq import RabbitMQ

from constant import MqConstant
from .app import get_app_instance
from .config import GLOBAL_CONFIG, INSTANCE

mqConfig = GLOBAL_CONFIG.get("RABBITMQ")


def get_mq_instance():
    app = get_app_instance()
    app.config.setdefault("RABMQ_RABBITMQ_URL",
                          "amqp://{}:{}@{}:{}/{}"
                          .format(mqConfig.get("username"),
                                  mqConfig.get("password"),
                                  mqConfig.get("host"),
                                  mqConfig.get("port"),
                                  mqConfig.get("virtual-host"))
                          )
    app.config.setdefault("RABMQ_SEND_EXCHANGE_NAME",
                          MqConstant.EVENT_DIRECT_EXCHANGE_NAME)
    app.config.setdefault("RABMQ_SEND_EXCHANGE_TYPE",
                          MqConstant.EVENT_EXCHANGE_TYPE)
    mq = INSTANCE.get("mq")

    if mq is None:
        mq = RabbitMQ()
        mq.init_app(app)

    return mq
