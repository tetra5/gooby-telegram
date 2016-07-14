#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging
from importlib import import_module

from settings import Settings


log = logging.getLogger('Telegooby.PluginManager')


class PluginManager(object):
    def __init__(self, bot):
        self.bot = bot
        self._plugins = []
        self._load_plugins()

    @property
    def plugins(self):
        yield from self._plugins

    @property
    def handlers(self, method='on_chat_message'):
        yield from (getattr(plugin, method) for plugin in self.plugins)

    def _load_plugins(self):
        plugins_dir = Settings.plugins_directory
        plugin_dirs = []

        # Sanity check.
        for possible_path in (p for p in plugins_dir.iterdir() if p.is_dir()):
            if possible_path.glob('__init__.py'):
                plugin_dirs.append(possible_path)

        # Actual import.
        for path in plugin_dirs:
            mod = import_module('{}.{}'.format(plugins_dir.stem, path.stem))
            for entity in dir(mod):
                if entity.lower() == path.stem.lower():
                    plugin_class = getattr(mod, entity)
                    plugin_name = plugin_class.__name__
                    if plugin_class:
                        log.info("Installing {} ...".format(plugin_name))
                        self._plugins.append(plugin_class(self.bot, path.stem))
                        log.info("Installed {}".format(plugin_name))

        if not self._plugins:
            log.warning("No suitable plugins found")
