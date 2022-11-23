# -*- coding: utf-8 -*-
"""
Default configuration for the REST API
"""
import os

GLOBAL_CONFIG = {
    "APP_NAME": "htcpmd-aiida-server",
    "APP_CONFIG": {
        "ENV": "development",
        "DEBUG": True,  # use False for production
        "PROPAGATE_EXCEPTIONS": True,  # serve REST exceptions to client
        # instead of generic 500 internal server error,
        "HOST": "127.0.0.1",
        "PORT": 9099
    },
    "API_CONFIG": {
        "LIMIT_DEFAULT": 400,  # default records total
        "PERPAGE_DEFAULT": 20,  # default records per page
        "PREFIX": "",  # prefix for all URLs
        "VERSION": "0.0.1",
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
        "group": "DEFAULT_GROUP",
        "server_name": "htcpmd-aiida-server",
        "data_id": "htcpmd-aiida-server.json",
        "username": "nacos",
        "password": "nacos",
    },
    "REDIS": {
        "host": "localhost",
        "port": "6379",
        "db": "0",
        "username": "",
        "password": ""
    }
}

INSTANCE = {"service": None, "api": None}
