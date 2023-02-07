# -*- coding: utf-8 -*-
"""
Default configuration for the REST API
"""
import os

# TODO: function to check valid of CONFIG

GLOBAL_CONFIG = {
    "APP_NAME": "htcpmd-aiida-server-20629461ac32465da7c37c418912a499",
    "APP_CONFIG": {
        "ENV": "development",
        "DEBUG": True,  # use False for production
        "PROPAGATE_EXCEPTIONS": True,  # serve REST exceptions to client
        # instead of generic 500 internal server error,
        "SERVER_NAME": "localhost:9099",
        "HOST": "localhost",
        "PORT": 9099,
        # "UPLOAD_FOLDER": ""
        # "MAX_CONTENT_LENGTH": ""
    },
    "API_CONFIG": {
        "limit_default": 400,  # default records total
        "perpage_default": 20,  # default records per page
        "prefix": "",  # prefix for all URLs,
        "version": "2.0",
        "doc": "/doc",
        "default_swagger_filename": "/v2/api-docs",
        "swagger_base_path": "/aiida-server/20629461ac32465da7c37c418912a499"
    },
    "CLI_DEFAULTS": {
        "HOST_NAME": "127.0.0.1",
        "PORT": 5000,
        "CONFIG_DIR": os.path.dirname(os.path.abspath(__file__)),
        "WSGI_PROFILE": False,
        "HOOKUP_APP": True,
        "CATCH_INTERNAL_SERVER": False,
        "POSTING": True,
        # Include POST endpoints (currently only /querybuilder)
    },
    # use 'asinput' or 'default'
    "SERIALIZER_CONFIG": {"datetime_format": "default"},
    "CACHE_CONFIG": {"CACHE_TYPE": "memcached"},
    "CACHING_TIMEOUTS": {  # Caching timeouts in seconds
        "nodes": 10,
        "users": 10,
        "calculations": 10,
        "computers": 10,
        "datas": 10,
        "groups": 10,
        "codes": 10,
    },
    # IO tree
    "MAX_TREE_DEPTH": 5,
    # Nacos
    "NACOS": {
        "host": "localhost",
        "port": "8849",
        "server_addresses": "127.0.0.1:8849",
        "namespace": "public",
        # "group": "AIIDA_SERVER",
        "group": "DEFAULT_GROUP",
        "server_name": "htcpmd-aiida-server-20629461ac32465da7c37c418912a499",
        "data_id": "htcpmd-aiida-server-20629461ac32465da7c37c418912a499.json",
        "username": "nacos",
        "password": "nacos",
    },
    # Database
    "DATABASE": {
        "SQLALCHEMY_DATABASE_URI":
            "mysql+pymysql://root:root@localhost/htcpmd-cloud?useUnicode=true"
            "&characterEncoding=utf-8&serverTimezone=Asia/Shanghai"
            "&useSSL=false"
    },
    # Redis
    "REDIS": {
        "host": "localhost",
        "port": "6379",
        "db": "0",
        "username": "",
        "password": ""
    },
    # RabbitMQ
    "RABBITMQ": {
        "host": "localhost",
        "port": "5672",
        "username": "htcpmd",
        "password": "htcpmd",
        "virtual-host": "/htcpmd",
        "listener": {
            "retry": True,
            "max-attempts": 3,
            "initial-interval": 5000,
            "max-interval": 50000
        }
    },
    "FILE_STORAGE": {
        "platform": "local",
        "storage-path": "D:/Temp/test"
    }
}

INSTANCE = {"service": None, "api": None}
