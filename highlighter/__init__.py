#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from plugin import Plugin
from utils import is_text_message


class Highlighter(Plugin):

    async def on_chat_message(self, message):
        if not is_text_message(message):
            return

        try:
            message_text = message['text']
        except KeyError:
            return
        for trigger in self.settings.get('triggers'):
            if trigger in message_text.lower():
                return "ОГОНЬ ПО ГОТОВНОСТИ! " + self.settings.get('players')
