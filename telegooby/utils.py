#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import telepot

from const import CONTENT_TYPE_TEXT


def content_type(message):
    return telepot.glance(message)[0]


def is_text_message(message):
    return content_type(message) == CONTENT_TYPE_TEXT
