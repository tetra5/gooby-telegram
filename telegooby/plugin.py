#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging

import yaml

from settings import Settings


class Plugin(object):
    def __init__(self, plugin_root):
        self.log = logging.getLogger('Telegooby.Plugin.{}'.format(
            self.__class__.__name__))
        self.plugin_root = plugin_root
        self.settings = {}
        self._load_settings()

    def _load_settings(self):
        settings_path = (
            Settings.plugins_directory /
            self.plugin_root /
            Settings.plugin_settings_file
        ).absolute()

        try:
            self.settings = yaml.safe_load(settings_path.read_bytes()) or {}
            self.log.debug("Loaded settings: {}".format(self.settings))
        except Exception as e:
            self.log.warning("Could not load settings from {}: {}".format(
                settings_path,
                e,
            ))

    async def on_chat_message(self, message):
        raise NotImplementedError
