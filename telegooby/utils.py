#!/usr/bin/env python3
# -*- coding: utf-8 -*-


from queue import Empty
from asyncio.queues import QueueEmpty


class QueueDrainer(object):
    def __init__(self, queue):
        self.queue = queue

    def __iter__(self):
        while True:
            try:
                yield self.queue.get_nowait()
            except (Empty, QueueEmpty):
                break
