# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import json
import os
from typing import List

from ase.io import read as ase_read
from ase.spacegroup import spacegroup

from common.utils import FileUtil
from proxy import FileProxy


def _upload_file_b(filepath: str, filename: str, headers) -> dict:
    with open(filepath, mode="rb") as rf:
        resp: dict = json.loads(FileProxy.upload_file(
            {
                "file": (filename, rf)
            },
            headers=headers
        ))

    resList: List[dict] = resp.get("data")
    if resList and len(resList) > 0:
        return resList.pop()

    return None


def test():
    fileInfo = {'id': None, 'url': 'local-plus/63aefcd472e2006f40b3cdd4.vasp',
                'size': 340, 'filename': '63aefcd472e2006f40b3cdd4.vasp',
                'originalFilename': 'beta_Sn.vasp', 'basePath': 'local-plus/',
                'path': '', 'ext': 'vasp',
                'contentType': 'application/octet-stream',
                'platform': 'local-plus-1', 'thUrl': None, 'thFilename': None,
                'thSize': None, 'thContentType': None, 'objectId': None,
                'objectType': None, 'attr': {}, 'createTime': 1672412370808}
    headers = {
        'authorization':
            'eyJhbGciOiJIUzUxMiJ9'
            '.eyJ1c2VyX2lkIjoxLCJ1c2VyX2tleSI6IjE1OTJiNTRmLTA1YjAtNDM4NS04Y2RjLTUyMzgwYzZiZjhjMyIsInVzZXJuYW1lIjoiYWRtaW4ifQ.gdYwrSQpPXkZRFzr-Xio22621Jau-AI5EVNZu1FIKky6GfzZ93F_kdMaMsnCFmq_I1AwsF7rMoybcWQ7DgCIeg',
        'user_id': '1', 'group_id': '1',
        'user_key': '1592b54f-05b0-4385-8cdc-52380c6bf8c3',
        'X-Forwarded-For': '127.0.0.1', 'username': 'admin'}
    filePath = FileProxy.download_file(fileInfo)
    if filePath is None:
        raise Exception
    aseAtoms = ase_read(filePath)
    attr = {
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
    }
    # upload structure cover image
    tf_name, tf_path = FileUtil.get_temp_file_path(prefix="structure_",
                                                   suffix=".png")
    with open(tf_path, mode="w+b") as tf:
        aseAtoms.write(tf.name, format="png")
    # with open(tf.name, mode="rb") as rf:
    #     js = requests.post(
    #         "http://localhost:9090/common_file/upload",
    #         files=FileUtil.gen_upload_file_list([rf, ])
    #     ).json()
    #     print(js)
    resp = _upload_file_b(tf.name, tf_name, headers)
    print(resp)
    os.unlink(tf.name)
    print(os.path.isfile(tf.name))


if __name__ == '__main__':
    test()
