#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from queue import Queue
import logging

import telepot

import yaml

from settings import Settings
from utils import QueueDrainer


class Plugin(object):
    def __init__(self, plugin_root_dir):
        self.log = logging.getLogger('Telegooby.Plugin.{}'.format(
            self.__class__.__name__))
        self.plugin_root_dir = plugin_root_dir
        self.settings = []
        self.__load_settings()
        self.output = Queue()

    def __load_settings(self):
        settings_path = (
            Settings.plugins_directory /
            self.plugin_root_dir /
            Settings.plugin_settings_file
        ).absolute()

        try:
            self.settings = yaml.safe_load(settings_path.read_bytes())
            self.log.debug("Loaded settings: {}".format(self.settings))
        except Exception as e:
            self.log.warning("Could not load settings from {}: {}".format(
                settings_path,
                e,
            ))

    def flush_output_queue(self):
        yield from QueueDrainer(self.output)

    def on_chat_message(self, message):
        content_type, chat_type, chat_id = telepot.glance(message)

        if content_type != 'text':
            return
