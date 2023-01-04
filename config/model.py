# -*- coding: utf-8 -*-
"""Auto generated Google style docstrings.

Description
"""
import datetime

import sqlalchemy as sa

from .db import get_db_instance

db = get_db_instance()


class BaseModel(db.Model):
    id = sa.Column(sa.BigInteger, primary_key=True, autoincrement=True)
    uuid = sa.Column(sa.String, unique=True)
    createUser = sa.Column("create_user", sa.String, nullable=True)
    updateUser = sa.Column("update_user", sa.String, nullable=True)
    createTime = sa.Column("create_time", sa.DateTime,
                           default=datetime.datetime.now,
                           onupdate=datetime.datetime.now)
    updateTime = sa.Column("update_time", sa.DateTime,
                           default=datetime.datetime.now,
                           onupdate=datetime.datetime.now)
    verNo = sa.Column("ver_no", sa.Integer, default=1, autoincrement=True)
    delSts = sa.Column("del_sts", sa.Boolean, default=False)
