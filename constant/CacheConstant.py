# -*- coding: utf-8 -*-
"""系统缓存常量信息

redis key
"""


class CacheConstant:
    # 缓存有效期，默认720（分钟）
    EXPIRATION = 720

    # 缓存刷新时间，默认120（分钟）
    REFRESH_TIME = 120

    # 密码最大错误次数
    PASSWORD_MAX_RETRY_COUNT = 5

    # 密码锁定时间，默认10（分钟）
    PASSWORD_LOCK_TIME = 10

    # 权限缓存前缀
    LOGIN_TOKEN_KEY = "login_tokens:"

    # 验证码
    CAPTCHA_CODE_KEY = "captcha_codes:"

    # 参数管理
    SYS_CONFIG_KEY = "sys_config:"

    # 字典管理
    SYS_DICT_KEY = "sys_dict:"

    # 登录账户密码错误次数
    PWD_ERR_CNT_KEY = "pwd_err_cnt:"
