# -*- coding: utf-8 -*-
"""Nacos Client Function Implements

Override default implements of [KcangNacos](
https://github.com/KcangYan/nacos-python-sdk)
"""
import hashlib
import io
import json
import logging
import time
from typing import Any, Callable, Dict

import requests

from common import SecurityContextHolder
from constant import CommonConstant, TokenConstant, UserConstant


def get_common_headers():
    headers = {}
    headers.setdefault(UserConstant.USER_ID_FIELD_NAME,
                       SecurityContextHolder.get_user_id())
    headers.setdefault(UserConstant.USER_KEY_FIELD_NAME,
                       SecurityContextHolder.get_user_key())
    headers.setdefault(UserConstant.USERNAME_FIELD_NAME,
                       SecurityContextHolder.get_username())
    headers.setdefault(TokenConstant.AUTHENTICATION,
                       SecurityContextHolder.get_token())
    headers.setdefault("X-Forwarded-For", SecurityContextHolder.get(
        UserConstant.REQUEST_ADDR_FIELD_NAME))
    headers.setdefault(CommonConstant.FROM_SOURCE_FIELD_NAME,
                       CommonConstant.INNER_SOURCE_FIELD_NAME)

    return headers


def fallbackFun(*args, **kwargs):
    return "request Error"


def timeOutFun(*args, **kwargs):
    return "request time out"


class CustNacosBalanceClient:
    def __init__(self, ip="127.0.0.1", port=8848, serviceName="",
                 group="DEFAULT_GROUP", namespaceId="public", timeout=6,
                 fallbackFun=fallbackFun, timeOutFun=timeOutFun):
        self.ip = ip
        self.port = port
        self.serviceName = serviceName
        self.group = group
        self.namespaceId = namespaceId
        self.__LoadBalanceDict = {}
        self.timeout = timeout
        self.fallbackFun = fallbackFun
        self.timeOutFun = timeOutFun

    def __doRequest(self, method, url, requestParamJson, *args, **kwargs):
        if method == "GET" or method == "get":
            url = url + "/"
            for item in args:
                url = url + str(item) + "/"
            url = url[:-1]
            if kwargs.__len__() != 0:
                url = url + "?"
                for item in kwargs:
                    url = url + str(item) + "=" + str(kwargs[item]) + "&"
                url = url[:-1]
            return requests.get(url, timeout=self.timeout).text
        if method == "POST" or method == "post":
            if requestParamJson:
                header = {"Content-type": "application/json;charset=utf-8"}
                data = None
                for item in args:
                    data = item
                return requests.post(url, headers=header, data=json.dumps(data,
                                                                          ensure_ascii=False).encode(
                    "utf-8"), timeout=self.timeout).text
            else:
                files = {}
                for map in args:
                    for key in map:
                        files[key] = (None, map[key])
                return requests.post(url, files=files,
                                     timeout=self.timeout).text

    def __getAddress(self, serviceName, group, namespaceId):
        getProviderUrl = "http://" + self.ip + ":" + str(
            self.port) + "/nacos/v1/ns/instance/list"
        params = {
            "serviceName": serviceName,
            "groupName": group,
            "namespaceId": namespaceId
        }
        re = requests.get(getProviderUrl, params=params)
        try:
            msg = re.json()['hosts']
        except json.JSONDecodeError:
            msg = []
        hosts = []
        for item in msg:
            hosts.append({
                'ip': item['ip'],
                'port': item['port'],
                'healthy': item['healthy']
            })
        md5 = hashlib.md5()
        md5.update(json.dumps(hosts, ensure_ascii=False).encode("utf-8"))
        md5Content = md5.hexdigest()
        try:
            oldMd5 = self.__LoadBalanceDict[
                serviceName + group + namespaceId + "md5"]
        except KeyError:
            self.__LoadBalanceDict[
                serviceName + group + namespaceId + "md5"] = md5Content
            oldMd5 = ""
        if oldMd5 != md5Content:
            healthyHosts = []
            for host in msg:
                if host['healthy'] == True:
                    healthyHosts.append(host)
            self.__LoadBalanceDict[
                serviceName + group + namespaceId] = healthyHosts
            self.__LoadBalanceDict[
                serviceName + group + namespaceId + "index"] = 0

    def __loadBalanceClient(self, serviceName, group, namespaceId):
        try:
            x = int(time.time()) - self.__LoadBalanceDict[
                serviceName + group + namespaceId + "time"]
        except KeyError:
            x = 11
        if x > 10:
            self.__getAddress(serviceName, group, namespaceId)
            self.__LoadBalanceDict[
                serviceName + group + namespaceId + "time"] = int(time.time())

        index = self.__LoadBalanceDict[
            serviceName + group + namespaceId + "index"]
        l = len(self.__LoadBalanceDict[serviceName + group + namespaceId])
        if l == 0:
            logging.error(
                "无可用服务 serviceName: " + serviceName + ";group: " + group +
                ";namespaceId: " + namespaceId)
            return ""
        if index >= l:
            self.__LoadBalanceDict[
                serviceName + group + namespaceId + "index"] = 1
            return self.__LoadBalanceDict[serviceName + group + namespaceId][0][
                       'ip'] + ":" + str(
                self.__LoadBalanceDict[serviceName + group + namespaceId][0][
                    'port'])
        else:
            self.__LoadBalanceDict[
                serviceName + group + namespaceId + "index"] = index + 1
            return \
                self.__LoadBalanceDict[serviceName + group + namespaceId][
                    index][
                    'ip'] + ":" + str(
                    self.__LoadBalanceDict[serviceName + group + namespaceId][
                        index]['port'])

    def customRequestClient(self, method, url,
                            requestParamJson=False, https=False):
        def requestPro(f):
            def mainPro(*args, **kwargs):
                address = self.__loadBalanceClient(self.serviceName, self.group,
                                                   self.namespaceId)
                if address == "":
                    return
                else:
                    if https:
                        requestUrl = "https://" + address + url
                    else:
                        requestUrl = "http://" + address + url
                    try:
                        return self.__doRequest(method, requestUrl,
                                                requestParamJson, *args,
                                                **kwargs)
                    except requests.ConnectTimeout:
                        logging.exception("链接超时   ", exc_info=True)
                        return self.timeOutFun(self.serviceName, self.group,
                                               self.namespaceId, method, url)
                    except Exception as ex:
                        logging.exception("链接失败   ", exc_info=True)
                        return self.fallbackFun(self.serviceName, self.group,
                                                self.namespaceId, method, url,
                                                ex)

            mainPro.__name__ = f.__name__
            return mainPro

        return requestPro

    def __do_rpc(self, method: str, url: str, headers: Dict[str, Any],
                 requestParamJson: bool,
                 *args,
                 **kwargs):
        if method == "GET" or method == "get":
            url = url + "/"
            for item in args:
                url = url + str(item) + "/"
            url = url[:-1]
            if kwargs.__len__() != 0:
                url = url + "?"
                for item in kwargs:
                    url = url + str(item) + "=" + str(kwargs[item]) + "&"
                url = url[:-1]
            return requests.get(url, headers=headers, timeout=self.timeout).text
        if method == "POST" or method == "post":
            if requestParamJson:
                headers.update(
                    {"Content-type": "application/json;charset=utf-8"})
                data = None
                for item in args:
                    data = item
                return requests.post(url, headers=headers, data=json.dumps(
                    data, ensure_ascii=False).encode("utf-8"),
                                     timeout=self.timeout).text
            else:
                files = None
                data = None
                for map in args:
                    for key in map:
                        if CommonConstant.FORM_DATA_FILE_KEY == key:
                            if isinstance(map[key], list):
                                files = map[key]
                            elif isinstance(map[key], io.BufferedReader):
                                files = {
                                    key: (
                                        CommonConstant.FORM_DATA_FILE_KEY,
                                        map[key])
                                }
                            else:
                                files = {key: map[key]}
                return requests.post(url,
                                     headers=headers,
                                     files=files,
                                     data=data,
                                     timeout=self.timeout).text

    def remote_func_call(self, method: str, url: str,
                         headers: Dict[str, Any] = None,
                         is_json=False, https=False,
                         rpcFun: Callable = None,
                         timeOutFun: Callable = None,
                         fallbackFun: Callable = None
                         ):
        if headers is None:
            headers = get_common_headers()

        def requestPro(f):
            def mainPro(*args, **kwargs):
                address = self.__loadBalanceClient(self.serviceName,
                                                   self.group,
                                                   self.namespaceId)
                if address == "":
                    return
                else:
                    if https:
                        requestUrl = "https://" + address + url
                    else:
                        requestUrl = "http://" + address + url
                    try:
                        # get headers set in called func
                        if "headers" in kwargs:
                            headers.update(kwargs.pop("headers"))

                        if rpcFun:
                            return rpcFun(method, requestUrl, headers,
                                          is_json, *args, **kwargs)
                        return self.__do_rpc(method, requestUrl, headers,
                                             is_json, *args, **kwargs)
                    except requests.ConnectTimeout:
                        logging.exception("链接超时   ", exc_info=True)
                        if timeOutFun:
                            return timeOutFun(self.serviceName, self.group,
                                              self.namespaceId, method, url)
                        return self.timeOutFun(self.serviceName, self.group,
                                               self.namespaceId, method,
                                               url)
                    except Exception as ex:
                        logging.exception("链接失败   ", exc_info=True)
                        if fallbackFun:
                            return fallbackFun(self.serviceName,
                                               self.group,
                                               self.namespaceId, method,
                                               url, ex)
                        return self.fallbackFun(self.serviceName,
                                                self.group,
                                                self.namespaceId, method,
                                                url, ex)

            mainPro.__name__ = f.__name__
            return mainPro

        return requestPro
