#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import logging.config
import logging
import asyncio

import telepot.aio
from telepot.exception import TelegramError

from settings import Settings, LOGGING_SETTINGS
from pluginmanager import PluginManager


class Telegooby(telepot.aio.Bot):
    def __init__(self, token):
        super(Telegooby, self).__init__(token)
        for path in (Settings.cache_directory, Settings.logs_directory):
            path.mkdir(parents=True, exist_ok=True)
        self._plugin_manager = PluginManager(self)

    async def on_chat_message(self, message):
        chat_id = message['chat']['id']

        async_handlers = [h(message) for h in self._plugin_manager.handlers]

        for future_result in asyncio.as_completed(async_handlers):
            try:
                await self.sendMessage(chat_id, await future_result)
            except TelegramError as e:
                # Result is empty due to unfinished async task.
                if e.error_code == 400:
                    pass
                else:
                    raise

    async def on_edited_chat_message(self, message):
        pass


if __name__ == '__main__':
    logging.config.dictConfig(LOGGING_SETTINGS)
    log = logging.getLogger('Telegooby')
    log.info("Starting up")
    log.info("Cache directory {}".format(Settings.cache_directory))
    log.info("Logs directory {}".format(Settings.logs_directory))
    telegooby = Telegooby(Settings.token)
    event_loop = asyncio.get_event_loop()
    event_loop.create_task(telegooby.message_loop())
    log.info("Entering asyncio event loop. Press CTRL+C to quit")
    try:
        event_loop.run_forever()
    finally:
        log.info("Shutting down")
        event_loop.close()
        logging.shutdown()
