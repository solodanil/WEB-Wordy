import requests
import json

import translators as ts
from emoji_translate import Translator


def google_dict(word, lang='en_US'):
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}').json()
    print(response)
    return response


def translate(word, lang='ru'):
    return ts.google(word, to_language=lang)


def emoji(word):
    emo = Translator(exact_match_only=False)
    return emo.emojify(word)


if __name__ == '__main__':
    print(translate('word'))
    print(emoji('hello'))
