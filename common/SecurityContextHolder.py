# -*- coding: utf-8 -*-
"""Thead Independent User Info Holder.

:var:
        local (:obj:`Thread.local`): Thread local variable to store data.
            local.user (dict): dict that stores the login user info
"""
import threading

from constant import TokenConstant, UserConstant

local = threading.local()


class SecurityContextHolder:
    """Maintain User Info of once request with a thread local variable\
    """

    @staticmethod
    def set_local_dict(data: dict):
        local.user = data

        return local.user

    @staticmethod
    def get_local_dict():
        try:
            if local.user is None:
                raise AttributeError()
        except AttributeError:
            local.user = {}

        return local.user

    @staticmethod
    def get(key: str):
        user = SecurityContextHolder.get_local_dict()
        return user.get(key, None)

    @staticmethod
    def set(key: str, value: any):
        user = SecurityContextHolder.get_local_dict()
        user.setdefault(key, value)

    @staticmethod
    def get_username() -> str:
        return SecurityContextHolder.get(UserConstant.USERNAME_FIELD_NAME)

    @staticmethod
    def get_user_id() -> str:
        return SecurityContextHolder.get(UserConstant.USER_ID_FIELD_NAME)

    @staticmethod
    def get_user_key() -> str:
        return SecurityContextHolder.get(UserConstant.USER_KEY_FIELD_NAME)

    @staticmethod
    def get_login_user() -> dict:
        """return login user info

        Returns:
            dict: login user info
        """
        return SecurityContextHolder.get(UserConstant.LOGIN_USER_FIELD_NAME)

    @staticmethod
    def get_token() -> str:
        return SecurityContextHolder.get(TokenConstant.AUTHENTICATION)

    @staticmethod
    def set_username(username: str):
        return SecurityContextHolder.set(UserConstant.USERNAME_FIELD_NAME,
                                         username)

    @staticmethod
    def set_user_id(user_id: str):
        SecurityContextHolder.set(UserConstant.USER_ID_FIELD_NAME, user_id)

    @staticmethod
    def set_user_key(user_key: str):
        SecurityContextHolder.set(UserConstant.USER_KEY_FIELD_NAME, user_key)

    @staticmethod
    def set_login_user(user: dict):
        SecurityContextHolder.set(UserConstant.LOGIN_USER_FIELD_NAME, user)

    @staticmethod
    def set_token(token: str):
        SecurityContextHolder.set(TokenConstant.AUTHENTICATION, token)

    @staticmethod
    def clear():
        del local.user
