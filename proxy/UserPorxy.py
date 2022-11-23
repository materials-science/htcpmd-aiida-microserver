# -*- coding: utf-8 -*-
"""Example Google style docstrings.

Example module
"""
from config import GLOBAL_CONFIG
from libs.nacos import CustNacosBalanceClient

NACOS = GLOBAL_CONFIG.get("NACOS")

SERVER_NAME = "ruoyi-system"

client = CustNacosBalanceClient(ip=NACOS.get("host"), port=NACOS.get("port"),
                                serviceName=SERVER_NAME)


@client.remote_func_call(method="GET", url="/user/profile")
def get_user_info():
    pass
