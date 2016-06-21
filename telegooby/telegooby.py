#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging.config
import logging

import asyncio

import telepot.async

from settings import Settings, LOGGING_SETTINGS
from pluginmanager import PluginManager
from utils import QueueDrainer


class Telegooby(telepot.async.Bot):
    def __init__(self, token):
        super(Telegooby, self).__init__(token)
        self.plugin_manager = PluginManager()
        self.output_queue = asyncio.Queue()
    
    async def on_chat_message(self, message):
        chat_id = message['chat']['id']

        for plugin in self.plugin_manager.plugins:
            plugin.on_chat_message(message)
            for item in plugin.flush_output_queue():
                self.output_queue.put_nowait(item)

        for message in QueueDrainer(self.output_queue):
            await self.sendMessage(chat_id, message)

    async def on_edited_chat_message(self, message):
        pass


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_SETTINGS)
    log = logging.getLogger('Telegooby')
    log.info("Starting up")
    telegooby = Telegooby(Settings.token)
    loop = asyncio.get_event_loop()
    loop.create_task(telegooby.message_loop())
    log.info("Entering event loop. Press CTRL+C to quit")
    loop.run_forever()
