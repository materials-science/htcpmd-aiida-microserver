# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import json

from common import SecurityContextHolder
from common.utils import IDUtil, Utils
from config import mq, redis_client
from constant import CacheConstant, TokenConstant, UserConstant


class EventUtil:
    @staticmethod
    def _get_event_user_info(headers: dict):
        user_id = headers.get(UserConstant.USER_ID_FIELD_NAME)
        if user_id:
            SecurityContextHolder.set_user_id(user_id)
        user_key = headers.get(UserConstant.USER_KEY_FIELD_NAME)
        if user_key:
            SecurityContextHolder.set_user_key(user_key)
        user_name = headers.get(UserConstant.USERNAME_FIELD_NAME)
        if user_name:
            SecurityContextHolder.set_username(user_name)
        user_ip = headers.get(UserConstant.REQUEST_ADDR_FIELD_NAME)
        if user_name:
            SecurityContextHolder.set(UserConstant.REQUEST_ADDR_FIELD_NAME, user_ip)

        token = headers.get(TokenConstant.AUTHENTICATION)

        if token and str.startswith(token, TokenConstant.TOKEN_PREFIX):
            token = str.removeprefix(token, TokenConstant.TOKEN_PREFIX)

        if token:
            claims = Utils.parse_token(token)
            user_key = claims.get(UserConstant.USER_KEY_FIELD_NAME)
            login_user = redis_client.get(
                CacheConstant.LOGIN_TOKEN_KEY + user_key)
            SecurityContextHolder.set_login_user(login_user)
            SecurityContextHolder.set_token(token)

        SecurityContextHolder.set("headers", headers)

    @staticmethod
    def pre_event_handler(*args):
        """
        to parse userinfo form `headers` filed
        :param args:
        :return:
        """

        def decorator(func):
            def _handler(body, message):
                event: dict = json.loads(body)
                message_id: str = message.properties.get("message_id", "")
                headers: dict = message.headers
                headers.update(event.get("headers", {}))
                data: dict = event.get("data", {})

                return func(data=data, headers=headers,
                            message_id=message_id, message=message)

            return _handler

        return decorator

    @staticmethod
    def send(data, headers, routing_key, exchange_name=None,
             exchange_type=None, mq_headers=None):
        mq.send(
            body={
                "message_id": IDUtil.simple_uuid(),
                "headers": headers,
                "data": data
            },
            routing_key=routing_key,
            exchange_name=exchange_name,
            exchange_type=exchange_type,
            headers=mq_headers
        )
