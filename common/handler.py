# -*- coding: utf-8 -*-
"""Flask Request and Response Handlers.
"""

from flask import current_app as app
from flask import request

from common import UserContextHolder
from common.utils import Utils
from config import redis_client
from constant import CacheConstant, UserConstant


def get_req_user_info(req):
    """get user info from http request header

    Args:
        req (request):
    """
    UserContextHolder.set_user_id(
        Utils.get_header(req, UserConstant.USER_ID_FIELD_NAME))
    UserContextHolder.set_user_key(
        Utils.get_header(req, UserConstant.USER_KEY_FIELD_NAME))
    UserContextHolder.set_username(
        Utils.get_header(req, UserConstant.USERNAME_FIELD_NAME))
    UserContextHolder.set(UserConstant.REQUEST_ADDR_FIELD_NAME,
                          req.remote_addr.__str__())

    token = Utils.get_token(req)

    if token:
        claims = Utils.parse_token(token)
        user_key = claims.get(UserConstant.USER_KEY_FIELD_NAME)
        login_user = redis_client.get(CacheConstant.LOGIN_TOKEN_KEY + user_key)
        UserContextHolder.set_login_user(login_user)
        UserContextHolder.set_token(token)


@app.before_request
def pre_request_handler():
    """Request 请求预处理

    Note:
        set strict_slashes = False 解决 url访问资源根路径若无"/", flask会做一次转发请求,
        转发的请求未携带用户信息的问题
    """
    get_req_user_info(request)


@app.after_request
def after_request_handler(response):
    """

    TODO:
        1. clear thread local UserContextHolder to avoid reusing the resident
        variable in the same thread by a new request
    """
    UserContextHolder.clear()

    return response
