# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import os
import shutil
from shutil import copyfileobj

import requests

from common.utils import FileUtil
from config import GLOBAL_CONFIG
from libs.nacos import CustNacosBalanceClient

NACOS = GLOBAL_CONFIG.get("NACOS")

SERVER_NAME = "htcpmd-center"

client = CustNacosBalanceClient(ip=NACOS.get("host"), port=NACOS.get("port"),
                                serviceName=SERVER_NAME)

_localPath = GLOBAL_CONFIG.get("FILE_STORAGE").get("storage-path")


def _get_file_fullpath(fileInfo: dict) -> str:
    """

    :param fileInfo:
    :return: file local full path
    """
    return os.path.join(_localPath,
                        fileInfo.get("basePath"),
                        fileInfo.get("filename"))


def download_file(fileInfo: dict) -> str:
    """

    :param fileInfo:
    :return: file local path
    """
    url = fileInfo.get("url")
    tf_name, tf_path = FileUtil.get_temp_file_path(
        prefix="tmp_",
        suffix=fileInfo.get("ext"),
        createDir=True)
    if fileInfo.get("platform", "").find("local") == -1:  # remote storage
        with requests.get(url, stream=True) as fsrc, \
                open(tf_path, mode="w+b") as fdst:
            copyfileobj(fsrc.raw, fdst)
        return fdst.name
    else:  # local storage
        return shutil.copyfile(_get_file_fullpath(fileInfo), tf_path)


def download_file_to_str(fileInfo: dict) -> str:
    """

    :param fileInfo:
    :return: file content
    """
    if fileInfo.get("platform", "").find("local") == -1:  # remote storage
        url = fileInfo.get("url")
        with requests.get(url, stream=True) as response:
            return response.raw
    else:
        fileStr = ""
        with open(_get_file_fullpath(fileInfo), mode='r') as f:
            fileStr = f.read()

        return fileStr


@client.remote_func_call(method="POST", url="/common_file/upload")
def upload_file(formData: dict, headers=None):
    """

    :param formData: { "file": List[fileObj] }
    :param headers: customized headers
    :return:
    """
    pass
