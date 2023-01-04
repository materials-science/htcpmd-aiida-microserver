# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import json
import os
import shutil
from datetime import datetime
from typing import List

import ase
from ase.io import read as ase_read
from ase.spacegroup import spacegroup

from common.event import EventUtil
from common.utils import FileUtil, IDUtil, UnCompress
from config import GLOBAL_CONFIG, log, mq
from config import redis_client as redis
from constant import CommonConstant, MqConstant, UserConstant
from constant.BizJobConstant import BizJobConstant, BizJobStatusEnum
from constant.StructureConstant import DiagramFiled
from proxy import FileProxy

APP_NAME = GLOBAL_CONFIG.get("APP_NAME")


class LogPush:
    APP_NAME = APP_NAME
    key = ""

    def __init__(self, key: str, func_name=None):
        self.key = key
        self.func_name = func_name

    def __push(self, type: str, text: str):
        if self.func_name:
            redis.rpush(self.key,
                        json.dumps(
                            f"[{type}] [{self.APP_NAME}] [{self.func_name}]"
                            f" {text}")
                        )
        else:
            redis.rpush(self.key,
                        json.dumps(f"[{type}] [{self.APP_NAME}] {text}")
                        )

    def info(self, text: str):
        self.__push('INFO', text)

    def error(self, text: str):
        self.__push('ERROR', text)

    def warn(self, text: str):
        self.__push('WARNING', text)

    @staticmethod
    def info_(key: str, text: str):
        redis.rpush(key, json.dumps(f"[INFO] [{APP_NAME}] {text}"))

    @staticmethod
    def error_(key: str, text: str):
        redis.rpush(key, json.dumps(f"[ERROR] [{APP_NAME}] {text}"))


def _add_failed_to_parse_structure_file_log(logPush: LogPush, fileInfo: dict,
                                            err: str = ""):
    logPush.error(
        "Failed to parse structure `{}`, of which url is `{}`, "
        "error msg is {}. "
        .format(fileInfo.get("originalFilename"), fileInfo.get("url"), err))


def _upload_file_b(filepath: str, headers, filename: str = None) -> dict:
    with open(filepath, mode="rb") as rf:
        resp: dict = json.loads(FileProxy.upload_file(
            {
                CommonConstant.FORM_DATA_FILE_KEY:
                    (filename if filename else
                     os.path.basename(filepath)
                     , rf)
            },
            headers=headers
        ))

    resList: List[dict] = resp.get("data")
    if resList and len(resList) > 0:
        return resList.pop()

    return None


@mq.queue(exchange_name=MqConstant.EVENT_DIRECT_EXCHANGE_NAME,
          queue_name=MqConstant.STRUCTURE_UPLOAD_QUEUE_NAME,
          routing_key=MqConstant.STRUCTURE_UPLOAD_QUEUE_NAME,
          exchange_type=MqConstant.EVENT_EXCHANGE_TYPE)
@EventUtil.pre_event_handler()
def upload_structures(data: dict, headers: dict, message_id: str):
    bizJobId: str = data.get("bizJobId")
    fileList: List[dict] = data.get("fileList")
    group: str = data.get("group")
    structureList: List[dict] = list()
    bizJobKey = f"{BizJobConstant.REDIS_KEY}:{bizJobId}"
    bizJobLogKey = f"{bizJobKey}:logs"
    logPush = LogPush(key=bizJobLogKey, func_name="upload_structures")

    if not redis.exists(bizJobKey):
        log.error(
            f"Invalid BizJob info of {bizJobKey}, nothing have to do.")
        return True

    if not fileList:
        logPush.info(
            f"[INFO] {APP_NAME} received empty fileList, nothing have to do.")
        return True

    logPush.info("Start to parse structure files.")

    redis.hset(bizJobKey, "status", BizJobStatusEnum.RUNNING.value)
    redis.hset(bizJobKey, "statusMsg", BizJobStatusEnum.RUNNING.name)

    # 处理结构文件
    for fileInfo in fileList:
        strucInfo = {}
        try:
            strucInfo["filepath"] = fileInfo.get("url")
            filePath = FileProxy.download_file(fileInfo)
            if filePath is None:
                raise Exception
            aseAtoms = ase_read(filePath)
            strucInfo.update({
                "cell": aseAtoms.get_cell().array.tolist(),
                "elements": aseAtoms.get_chemical_symbols(),
                "number_of_atoms": aseAtoms.get_global_number_of_atoms(),
                "volume": aseAtoms.get_volume(),
                "spacegroup": spacegroup.get_spacegroup(aseAtoms).no,
                "reciprocal_cell": aseAtoms.cell.reciprocal().array.tolist(),
                "formula": aseAtoms.symbols.get_chemical_formula(),
                "center_of_mass": aseAtoms.get_center_of_mass().tolist(),
                "pbc": aseAtoms.get_pbc().tolist(),
                "positions": aseAtoms.get_positions().tolist(),
            })
            logPush.info(
                f"parsed structure {aseAtoms.symbols.get_chemical_formula()} .")

            if fileInfo.get("ext") != "cif":
                # upload structure cif format
                tf_name, tf_path = FileUtil.get_temp_file_path(
                    prefix="structure_",
                    suffix=".cif")
                with open(tf_path, mode="w+b") as tf:
                    aseAtoms.write(tf.name, format="cif")
                resp = _upload_file_b(tf.name, headers)
                if resp:
                    strucInfo["filepath"] = resp.get("url")
                    logPush.info("Generated cif format file for this "
                                 "structure.")
                    del resp
                del tf_name
                del tf_path

            # upload structure cover image
            tf_name, tf_path = FileUtil.get_temp_file_path(prefix="structure_",
                                                           suffix=".png")
            with open(tf_path, mode="w+b") as tf:
                aseAtoms.write(tf.name, format="png")
            resp = _upload_file_b(tf.name, headers)
            if resp:
                strucInfo["cover_img"] = resp.get("url")
                logPush.info("Generated cover image for this structure.")
                del resp
            del tf_name
            del tf_path
        except Exception as err:
            log.error(f"Failed to parse structure file, err is : {err}.")
            _add_failed_to_parse_structure_file_log(logPush, fileInfo, str(err))
            continue
        structureList.append(strucInfo)

    # 发布结构文件解析完成事件
    logPush.info(f"共完成 {len(structureList)} 结构文件解析.")

    redis.hset(bizJobKey, "status", BizJobStatusEnum.WAITING.value)
    redis.hset(bizJobKey, "statusMsg", BizJobStatusEnum.WAITING.name)

    EventUtil.send(
        data={
            "bizJobId": bizJobId,
            "fileList": fileList,
            "structureList": structureList,
            "group": group
        },
        headers=headers,
        routing_key=MqConstant.STRUCTURE_UPLOAD_CALLBACK_QUEUE_NAME,
        exchange_name=MqConstant.EVENT_DIRECT_EXCHANGE_NAME
    )

    return True


def import_structure_from_aiida(data: dict, headers: dict, message_id: str):
    bizJobId: str = data.get("bizJobId")
    group: str = data.get("group")
    structureList: List[dict] = list()
    bizJobKey = f"{BizJobConstant.REDIS_KEY}:{bizJobId}"
    bizJobLogKey = f"{bizJobKey}:logs"
    logPush = LogPush(key=bizJobLogKey, func_name="import_structure_from_aiida")
    fileInfo: dict = data.get("file")
    user_id = headers.get(UserConstant.USER_ID_FIELD_NAME)
    arcPath = None
    tmp_dir = None
    try:
        arcPath = FileProxy.download_file(fileInfo)
        if arcPath is None:
            raise Exception
        else:
            tmp_dir = os.path.dirname(arcPath)
        uncompress = UnCompress(arcPath, "data")
        uncompress.extract()
    except Exception as exp:
        logPush.error(
            "Failed to uncompress file {}. With Exception {}".format(
                fileInfo.get("url"), exp
            )
        )
        redis.hset(bizJobKey, "status", BizJobStatusEnum.FAILED.value)
        redis.hset(bizJobKey, "statusMsg", BizJobStatusEnum.FAILED.name)
        if tmp_dir:
            shutil.rmtree(tmp_dir, ignore_errors=True)
        return True

    structures_json_path = os.path.join(tmp_dir, "data/structures.json")
    if os.path.isfile(structures_json_path):
        logPush.info("reading structures.json...")
        with open(structures_json_path, "r", encoding="utf8") as fi:
            stru_data = json.loads(fi.read())
            for stru_info in stru_data:
                strucInfo = {}
                label = stru_info["structure_label"]
                strucFormat = None
                if os.path.isfile(
                        os.path.join(tmp_dir,
                                     "data/structures/{}.xsf".format(label))
                ):
                    stru_filepath = os.path.join(
                        tmp_dir, "data/structures/{}.xsf".format(label)
                    )
                    strucFormat = "xsf"
                elif os.path.isfile(
                        os.path.join(tmp_dir,
                                     "data/structures/{}.cif".format(label))
                ):
                    stru_filepath = os.path.join(
                        tmp_dir, "data/structures/{}.cif".format(label)
                    )
                    strucFormat = "cif"
                elif os.path.isfile(
                        os.path.join(tmp_dir,
                                     "data/structures/{}.vasp".format(label))
                ):
                    stru_filepath = os.path.join(
                        tmp_dir, "data/structures/{}.vasp".format(label)
                    )
                    strucFormat = "vasp"
                elif os.path.isfile(
                        os.path.join(tmp_dir,
                                     "data/structures/{}.poscar".format(label))
                ):
                    stru_filepath = os.path.join(
                        tmp_dir, "data/structures/{}.poscar".format(label)
                    )
                    strucFormat = "vasp"
                else:
                    logPush.warn("no structure file found.")
                    continue

                logPush.info(f"parsing structure {label}")

                # get structure attr
                try:
                    aseAtoms = ase.io.read(stru_filepath, format=strucFormat)

                    stru_png_path = os.path.join(tmp_dir,
                                                 "data/structures/{}.png"
                                                 .format(label))
                    stru_jpg_path = os.path.join(tmp_dir,
                                                 "data/structures/{}.jpg"
                                                 .format(label))
                    if os.path.isfile(stru_png_path):
                        resp = _upload_file_b(stru_png_path, headers)
                    elif os.path.isfile(stru_jpg_path):
                        resp = _upload_file_b(stru_jpg_path, headers)
                    else:
                        # upload structure cover image
                        tf_name, tf_path = FileUtil.get_temp_file_path(
                            prefix="structure_",
                            suffix=".png")
                        with open(tf_path, mode="w+b") as tf:
                            aseAtoms.write(tf.name, format="png")
                        resp = _upload_file_b(tf.name, headers)

                    if resp:
                        strucInfo["cover_img"] = resp.get("url")
                        logPush.info(
                            "Generated cover image for this structure.")
                        del resp

                    strucInfo.update(
                        {
                            "cell": aseAtoms.get_cell().array.tolist(),
                            "elements": aseAtoms.get_chemical_symbols(),
                            "number_of_atoms":
                                aseAtoms.get_global_number_of_atoms(),
                            "volume": aseAtoms.get_volume(),
                            "spacegroup": spacegroup.get_spacegroup(
                                aseAtoms).no,
                            "reciprocal_cell": aseAtoms.cell.reciprocal(

                            ).array.tolist(),
                            "formula":
                                aseAtoms.symbols.get_chemical_formula(),
                            "center_of_mass": aseAtoms.get_center_of_mass(

                            ).tolist(),
                            "pbc": aseAtoms.get_pbc().tolist(),
                            "positions": aseAtoms.get_positions().tolist(),
                        }
                    )

                    # upload structure cif format
                    tf_name, tf_path = FileUtil.get_temp_file_path(
                        prefix="structure_",
                        suffix=".cif")
                    with open(tf_path, mode="w+b") as tf:
                        aseAtoms.write(tf.name, format="cif")
                    resp = _upload_file_b(tf.name, headers)
                    if resp:
                        strucInfo["filepath"] = resp.get("url")
                        logPush.info("Generated cif format file for this "
                                     "structure.")
                        del resp
                    del tf_name
                    del tf_path
                except Exception as exp:
                    logPush.error(
                        "cannot parse structure info. {}. skip.".format(exp)
                    )
                    continue

                # get structure energy bands
                try:
                    bands_label = stru_info["bands_label"]
                    bands_filepath = os.path.join(
                        tmp_dir, "data/bands/{}_data.json".format(bands_label)
                    )
                    bands_uuid = IDUtil.simple_uuid()
                    if os.path.isfile(bands_filepath):
                        # upload bands data
                        resp = _upload_file_b(bands_filepath, headers)
                        if resp:
                            new_bands_filepath = resp.get("url")
                            logPush.info(
                                "Uploaded bands data for this structure.")
                            del resp

                        band_data = {
                            "createBy": user_id,
                            "type": "json",
                            "filepath": new_bands_filepath,
                            "uuid": bands_uuid,
                            "createTime": datetime.now(),
                            "data": "",
                            "field": DiagramFiled.band.name,
                            "description": DiagramFiled.band.value
                        }
                        strucInfo.update({"bandList": [band_data]})
                except Exception as exp:
                    logPush.error("cannot get bands info. {}".format(exp))

                # get Phonon Dispersion data
                try:
                    phonons_label = stru_info["phonons_label"]
                    phonons_filepath = os.path.join(
                        tmp_dir,
                        "data/phonons/{}_data.json".format(phonons_label)
                    )
                    phonons_uuid = IDUtil.simple_uuid()
                    if os.path.isfile(phonons_filepath):
                        # upload phonon dispersion data
                        resp = _upload_file_b(phonons_filepath, headers)
                        if resp:
                            new_phonons_filepath = resp.get("url")
                            logPush.info(
                                "Uploaded Phonon Dispersion data for this "
                                "structure.")
                            del resp

                        phonon_data = {
                            "createBy": user_id,
                            "type": "json",
                            "filepath": new_phonons_filepath,
                            "uuid": phonons_uuid,
                            "createTime": datetime.now(),
                            "data": "",
                            "field": DiagramFiled.phonon.name,
                            "description": DiagramFiled.phonon.value
                        }
                        strucInfo.update({
                            "phononList": [phonon_data]
                        })
                except Exception as exp:
                    logPush.error("can not get phonons info. {}".format(exp))

                structureList.append(strucInfo)
                logPush.info(f"parsed structure {label}")

        logPush.info(
            "Stats: import {} structures data, lost {}.".format(
                len(structureList), len(stru_data) - len(structureList)
            )
        )
    else:
        logPush.info("Stats: No available structures.json found.")

    redis.hset(bizJobKey, "status", BizJobStatusEnum.WAITING.value)
    redis.hset(bizJobKey, "statusMsg", BizJobStatusEnum.WAITING.name)

    EventUtil.send(
        data={
            "type": "aiida",
            "bizJobId": bizJobId,
            "structureList": structureList,
            "tags": data.get("tags"),
            "group": group
        },
        headers=headers,
        routing_key=MqConstant.STRUCTURE_IMPORT_CALLBACK_QUEUE_NAME,
        exchange_name=MqConstant.EVENT_DIRECT_EXCHANGE_NAME
    )

    shutil.rmtree(tmp_dir, ignore_errors=True)

    return True


@mq.queue(exchange_name=MqConstant.EVENT_DIRECT_EXCHANGE_NAME,
          queue_name=MqConstant.STRUCTURE_IMPORT_QUEUE_NAME,
          routing_key=MqConstant.STRUCTURE_IMPORT_QUEUE_NAME,
          exchange_type=MqConstant.EVENT_EXCHANGE_TYPE)
@EventUtil.pre_event_handler()
def import_structure(data: dict, headers: dict, message_id: str):
    _t = data.get("type")
    if _t == "aiida":
        return import_structure_from_aiida(data, headers, message_id)

    return True
