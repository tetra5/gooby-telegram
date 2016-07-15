#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re
import string
import random
import os
import pickle

from pony import orm

from plugin import Plugin
from utils import is_text_message
from settings import Settings
from database.models import Author, ChatMessage
from database import db


def url_filter(word):
    crap = ('http', 'ftp', 'www', 'mailto')
    return '' if any(substring in word.lower() for substring in crap) else word


def highlight_filter(word):
    return '' if word.startswith('@') else word


def sentence_normalizer(sentence):
    """
    >>> print(sentence_normalizer("чот рофл, ходил "))
    Чот рофл, ходил.
    >>> print(sentence_normalizer("как же так("))
    Как же так(
    >>> print(sentence_normalizer('Рофел'))
    Рофел.
    >>> print(sentence_normalizer('а'))
    А.
    >>> print(sentence_normalizer('.один... два, три .. четыре. пять'))
    Один... Два, три.. Четыре. Пять.
    >>> print(sentence_normalizer('///.'))
    <BLANKLINE>
    >>> print(sentence_normalizer('.'))
    <BLANKLINE>
    >>> print(sentence_normalizer('asdf ._.'))
    Asdf ._.
    """
    replacements = {
        '. _.': ' ._.',
    }
    pattern = re.compile(r'\w+', re.U)
    sentences = [word.strip() for word in re.split(r'(\.)', sentence) if word]
    ending = '.'

    output = []
    for word in sentences:
        if not output:
            if word == '.':
                continue
            output.append(word)
            continue
        if word != ending and output[-1][-1] == ending:
            output.append(word)
        if word == ending:
            output[-1] += word

    for i, s in enumerate(output):
        output[i] = output[i][0].upper() + output[i][1:]
        if not output[i].endswith(tuple(string.punctuation)):
            output[i] += ending

    if not pattern.match(' '.join(output)):
        return ''

    if not filter(None, ' '.join(output).split(ending)):
        return ''

    output = ' '.join(output)
    for old, new in replacements.items():
        output = output.replace(old, new)

    return output


def sentence_min_length_limiter(sentence):
    return '' if len(sentence.split()) < 2 else sentence


WORD_FILTERS = (highlight_filter, url_filter, )
SENTENCE_FILTERS = (sentence_min_length_limiter, sentence_normalizer, )


class MarkovChain(object):
    ENDING_CHARACTERS = ('!', '?', '.')
    RUSSIAN_ALPHABET = 'абвгдеёжзийклмнопрстуфхцчшщъыьэюя'
    ENGLISH_ALPHABET = string.ascii_lowercase
    ALPHABETIC = RUSSIAN_ALPHABET + ENGLISH_ALPHABET

    def __init__(self, order=1):
        self._order = order
        self.db = dict()
        self._order = 2
        self._used_first_keys = list()

    def generate_db(self, words):
        for i, word in enumerate(words[:-(self._order + 1)]):
            value_pos = i + self._order
            key = tuple(words[i:i + self._order])
            values = self.db.setdefault(key, list())
            values.append(words[value_pos])

    def _find_first_key(self):
        possible_keys = []
        for key in self.db.keys():
            first_word = key[0]
            last_word = key[-1]
            if key in self._used_first_keys:
                continue
            if not first_word.lower().startswith(tuple(self.ALPHABETIC)):
                continue
            if first_word.endswith(tuple(string.punctuation)):
                continue
            if first_word.startswith(tuple(string.punctuation)):
                continue
            if last_word.endswith(tuple(string.punctuation)):
                continue
            if first_word.istitle():
                possible_keys.append(key)
        if not possible_keys:
            possible_keys.extend(self.db.keys())
        first_key = random.choice(possible_keys)
        self._used_first_keys.append(first_key)
        return first_key

    def generate_sentence(self, max_len=8):
        key = self._find_first_key()
        words = list()
        words.append(key[0])
        while 1:
            possible_words = self.db.get(key)
            if not possible_words:
                break
            word = random.choice(list(possible_words))
            words.append(word)
            if word.endswith(self.ENDING_CHARACTERS) and len(words) > max_len:
                break
            key = key[1:] + (word, )
        return ' '.join(words)

    def generate_sentences(self, sentences_count=3, max_word_per_sentence=32):
        sentences = []
        for _ in range(sentences_count):
            sentence = self.generate_sentence()
            sentences.append(sentence)
            if len(sentence.split()) > max_word_per_sentence:
                break
        return sentences

    @classmethod
    def from_string(cls, text, order=1):
        obj = cls(order)
        obj.generate_db([w for w in text.split() if w])
        return obj

    @classmethod
    def from_textfile(cls, path, order=1):
        with open(os.path.abspath(path), mode='rb') as f:
            text = f.read().decode('utf-8')
        obj = cls.from_string(text, order)
        return obj


class RavingMarkov(Plugin):
    def __init__(self, bot, plugin_root):
        super(RavingMarkov, self).__init__(bot, plugin_root)
        db_file = Settings.cache_directory / '{}.sqlite'.format(self.plugin_root)
        self.pickle_file = Settings.cache_directory / '{}.pickle'.format(self.plugin_root)
        self.pickle_file.touch(0o666)
        db.bind('sqlite', str(db_file.absolute()), create_db=True)
        db.generate_mapping(create_tables=True)

    async def on_chat_message(self, message):
        if not is_text_message(message):
            return

        author_id = str(message['from']['id'])
        username = message['from']['username']

        message_id = message['message_id']
        chat_id = str(message['chat']['id'])
        timestamp = message['date']
        text = message['text']

        try:
            unpickled_data = pickle.loads(self.pickle_file.read_bytes())
        except EOFError:
            unpickled_data = {}

        with orm.db_session():
            author = Author.get(author_id=author_id)

            if not author:
                author = Author(author_id=author_id, username=username)
            else:
                author.username = username

            chat_message = ChatMessage(
                author=author,
                message_id=message_id,
                chat_id=chat_id,
                timestamp=timestamp,
                text=text,
            )

            db.commit()

            if any(t in text for t in self.settings['trigger_chat_commands']):
                messages = [self.process_text(m)
                            for m in orm.select(m.text for m in ChatMessage if m.chat_id == chat_id)]
                try:
                    mc = MarkovChain.from_string(' '.join(messages))
                    mc.db.update(unpickled_data)
                    self.pickle_file.write_bytes(pickle.dumps(mc.db, 4))
                    return ' '.join(mc.generate_sentences())
                except:
                    return

    @staticmethod
    def process_text(text):
        output = text
        for f in WORD_FILTERS:
            output = ' '.join(filter(None, [f(w) for w in output.split()]))
        for f in SENTENCE_FILTERS:
            output = f(output)
        return output


if __name__ == '__main__':
    import doctest
    doctest.testmod()
