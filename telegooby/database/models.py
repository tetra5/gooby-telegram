#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from pony import orm

from . import db


class Author(db.Entity):
    author_id = orm.Required(str, unique=True)
    username = orm.Required(str)
    messages = orm.Set('ChatMessage', reverse='author')


class ChatMessage(db.Entity):
    author = orm.Required('Author')
    message_id = orm.Required(int, unique=True)
    chat_id = orm.Required(str)
    timestamp = orm.Required(int)
    text = orm.Required(str)
