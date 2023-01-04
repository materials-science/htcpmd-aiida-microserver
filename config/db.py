# -*- coding: utf-8 -*-
"""Database configuration.

SQLAlchemy
"""
from flask_sqlalchemy import SQLAlchemy

from .app import get_app_instance
from .config import GLOBAL_CONFIG, INSTANCE


def get_db_instance():
    app = get_app_instance()
    app.config.update(GLOBAL_CONFIG.get("DATABASE"))
    db = INSTANCE.get("database")

    if db is None:
        db = SQLAlchemy(app=app)
        INSTANCE.setdefault("database", db)

    return db
