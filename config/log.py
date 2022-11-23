# -*- coding: utf-8 -*-
"""Log configuration.

@todo: use `python-logstash` to send logs to logstash
"""
import logging

log = logging.getLogger(__name__)
log.setLevel(logging.DEBUG)
