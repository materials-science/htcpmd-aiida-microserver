# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import json
import logging
import traceback
import uuid
from threading import RLock
from typing import Callable

from flask_rabmq import RabbitMQ
from flask_rabmq.exceptions import ExchangeNameError, RoutingKeyError
from flask_rabmq.utils import ExchangeType, is_py2, setup_method
from kombu import Connection
from kombu import Exchange
from kombu import Queue
from kombu.exceptions import KombuError
from kombu.mixins import ConsumerProducerMixin

from common import SecurityContextHolder

logger = logging.getLogger("flask_rabmq")


class CustConsumer(ConsumerProducerMixin):

    def __init__(self, connection, rpc_class_list):
        self.connection = connection
        self.rpc_class_list = rpc_class_list

    def get_consumers(self, consumer, channel):
        consumer_set = []
        for consumer_info in self.rpc_class_list:
            logger.info("consumer queue name: %s" % consumer_info['queue'])
            consumer_set.append(
                consumer(
                    queues=consumer_info['queue'],
                    callbacks=[consumer_info['callback']],
                    prefetch_count=1,  # 一个连接中只能有一个消息存在
                    auto_declare=False
                )
            )

        return consumer_set


class MyRabbitMQ(RabbitMQ):
    def init_app(self, app):
        self.app = app
        self.config = app.config
        self.listener_config = self.config.get("RABBITMQ", {}) \
            .get("listener", None)
        self.connection = Connection(self.config.get('RABMQ_RABBITMQ_URL'))
        self.consumer = CustConsumer(self.connection,
                                     self.message_callback_list)
        self.send_exchange_name = self.config.get('RABMQ_SEND_EXCHANGE_NAME')
        self.send_exchange_type = self.config.get(
            'RABMQ_SEND_EXCHANGE_TYPE') or ExchangeType.TOPIC
        self.wait_send_lock = RLock()

    def queue(
            self,
            exchange_name,
            routing_key,
            queue_name=None,
            exchange_type=None,
            process_alone=False,
            exception_handler=None
    ):
        """

        :param exchange_name:
        :param routing_key:
        :param queue_name:
        :param exchange_type:
        :param retry_count: 当消费方法返回结果为False的表达式时生效。
        :param process_alone: if True, queue is not durable.
        :return:
        """

        def decorator(func):
            self.add_message_rule(
                func,
                queue_name=queue_name,
                exchange_type=exchange_type,
                exchange_name=exchange_name,
                routing_key=routing_key,
                process_alone=process_alone,
                exception_handler=exception_handler
            )

            return func

        return decorator

    @setup_method
    def add_message_rule(
            self, func, queue_name, routing_key,
            exchange_name, exchange_type=ExchangeType.DEFAULT,
            process_alone=False,
            exception_handler: Callable = None
    ):
        if not queue_name:
            queue_name = func.__name__
        if process_alone:
            queue_name = "%s_%s" % (
                queue_name, str(uuid.uuid4()).replace("-", ""))
        if not routing_key:
            raise RoutingKeyError('routing_key 没有指定')

        if not exchange_name:
            raise ExchangeNameError('exchange_name 没有指定')

        retry_count = 0
        if self.listener_config:
            if self.listener_config.get("retry"):
                retry_count = int(
                    self.listener_config.get("max-attempts"))

        def _handle_func_check(result, body, message):
            if result:
                message.ack()
                return True
            else:
                logger.info('no ack message')
                if retry_count > 0:
                    # resend message
                    if int(
                            message.headers.get('retry', 0)
                    ) < retry_count:
                        headers = message.headers
                        headers.update(
                            {'retry': int(message.headers.get('retry', 0)) + 1}
                        )
                        message.ack()
                        self.retry_send(body=body, queue_name=queue_name,
                                        headers=headers)

                        return False

                    # reach the max
                    logger.info('retry %s count handler failed: %s',
                                retry_count, body)

                message.ack()
                logger.info('event handler failed: %s', body)
                return True

        def _callback(body, message):
            try:
                SecurityContextHolder.set_local_dict(message.headers)
                logger.info('message handler start: %s', func.__name__)
                # try to parse body
                try:
                    logger.info('received message routing_key:%s, exchange:%s',
                                routing_key,
                                exchange_name)
                    logger.info('received data:%s', body)
                    if is_py2:
                        if isinstance(body, (str, eval('unicode'))):
                            parsed = json.loads(body).get('data')
                        else:
                            parsed = body.get('data')
                    else:
                        if isinstance(body, str):
                            parsed = json.loads(body).get('data')
                        else:
                            parsed = body.get('data')
                    if not parsed:
                        logger.warning('message body no `data`: %s', body)
                    if not message.properties.get('message_id'):
                        logger.warning('message no id: %s', json.dumps(
                            message.properties))
                except Exception as E:
                    logger.error('parse message body failed:%s', body)
                    message.ack()
                    return True
                # call func to handle message
                try:
                    if is_py2:
                        if not isinstance(body, (str, eval('unicode'))):
                            body = json.dumps(body)
                    else:
                        if not isinstance(body, str):
                            body = json.dumps(body)
                    with self.app.app_context():
                        result = func(body, message)
                    _handle_func_check(result, body, message)
                except KombuError:  # 不可预测的kombu错误
                    logger.error('Kombu Error pass: %s', traceback.format_exc())
                    return True
                except Exception as e:
                    logger.error('handler message failed: %s',
                                 traceback.format_exc())
                    # call exception handler if exist or just reject
                    if exception_handler:
                        try:
                            with self.app.app_context():
                                result = exception_handler(body, message)
                            _handle_func_check(result, body, message)
                        except Exception as e:
                            logger.error('exception_handler throw exception: '
                                         '%s',
                                         traceback.format_exc())
                            message.reject()
                            return True
                    # message.requeue()
                    try:
                        _handle_func_check(False, body, message)
                    except Exception as e:
                        message.reject()
                        return True
                finally:
                    logger.info('message handler end: %s', func.__name__)
            except Exception as e:
                logger.error('unknown error: %s' % traceback.format_exc())
                return True
            finally:
                SecurityContextHolder.clear()

        exchange = Exchange(name=exchange_name,
                            type=exchange_type or ExchangeType.DEFAULT)
        queue = Queue(name=queue_name, exchange=exchange,
                      routing_key=routing_key, auto_delete=process_alone)
        tmp_dict = {'queue': queue, 'callback': _callback}
        self.message_callback_list.append(tmp_dict)

    def send(self, body, routing_key, exchange_name=None, exchange_type=None,
             headers=None, **properties):
        exchange = Exchange(
            name=exchange_name or self.send_exchange_name,
            type=exchange_type or self.send_exchange_type,
            auto_delete=False,
            durable=True
        )

        properties["message_id"] = str(uuid.uuid4()).replace("-", "")
        with self.wait_send_lock:
            self.consumer.producer.publish(
                body=body,
                exchange=exchange,
                routing_key=routing_key,
                retry=True,
                headers=headers,
                declare=[exchange],
                **properties
            )
            logger.info('send data: %s', body)

    def retry_send(self, body, queue_name, headers=None, **properties):
        exchange = Exchange()
        properties["message_id"] = str(uuid.uuid4()).replace("-", "")
        with self.wait_send_lock:
            self.consumer.producer.publish(
                body=body,
                exchange=exchange,
                routing_key=queue_name,
                retry=True,
                headers=headers,
                **properties
            )
            logger.info('retry send data: %s', body)
