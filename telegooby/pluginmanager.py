#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import logging
from importlib import import_module

from settings import Settings


log = logging.getLogger('Telegooby.PluginManager')


class PluginManager(object):
    def __init__(self):
        self.plugins = list()
        self.load_plugins()

    def load_plugins(self):
        plugins_dir = Settings.plugins_directory
        plugin_dirs = []

        # Sanity check.
        for path in [p for p in plugins_dir.iterdir() if p.is_dir()]:
            if path.glob('__init__.py'):
                plugin_dirs.append(path)

        # Actual import.
        for path in plugin_dirs:
            mod = import_module('{}.{}'.format(plugins_dir.stem, path.stem))
            for entity in dir(mod):
                if entity.lower() == path.stem.lower():
                    plugin = getattr(mod, entity)
                    plugin_name = plugin.__name__
                    if plugin:
                        log.info("Installing {} ...".format(plugin_name))
                        self.plugins.append(plugin(path.stem))
                        log.info("Installed {}".format(plugin_name))

        if not self.plugins:
            log.warning("No plugins found")
