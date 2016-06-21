#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import os
from pathlib import Path


class Settings:
    token = os.environ.get('TELEGRAM_BOT_API_TOKEN')
    plugins_directory = Path('./plugins')
    plugin_settings_file = 'settings.yaml'


LOGGING_SETTINGS = {
    'version': 1,
    'disable_existing_loggers': True,
    'formatters': {
        'verbose': {
            'format': '%(asctime)-15s %(levelname)s %(name)s: %(message)s',
        },
        'brief': {
            'format': '%(levelname)-8s %(name)s: %(message)s',
        },
    },
    'handlers': {
        'console': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'stream': 'ext://sys.stdout',
        },
        'console_stderr': {
            'level': 'DEBUG',
            'class': 'logging.StreamHandler',
            'formatter': 'brief',
            'stream': 'ext://sys.stderr',
        },
    },
    'loggers': {
        'Telegooby': {
            'handlers': ['console', ],
            'level': 'DEBUG',
        },
        'asyncio': {
            'handlers': ['console_stderr', ],
            'level': 'DEBUG',
        },
    },
}

