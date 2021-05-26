import requests
import time

import translators as ts
from emoji_translate import Translator


def google_dict(word, lang='en_US'):
    """метод обращения к словарю google"""
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}').json()
    if 'title' in response:
        return False
    else:
        return response


def translate(word, lang='ru'):
    """Гугл переводчик"""
    return ts.google(word, to_language=lang)


def emoji(word):
    """Получение эмодзи по слову"""
    emo = Translator(exact_match_only=False)
    emoj = emo.emojify(word)
    if emoj == word.lower():
        emoj = ''
    return emoj


def search_image(word):
    """поиск картинки по слову"""
    response = requests.get(
        f'https://api.unsplash.com/search/photos?page=1&query={word}&client_id=LbDsTQQY_mSADos2tEp_Y_JXtseb7l92LtH0J0Z1KjY').json()
    image = response['results'][0]['urls']['raw']
    return image


def search_synonyms(dict_response):
    """Поиск синонимов слова"""
    if 'synonyms' in dict_response['meanings'][0]['definitions'][0]:
        synonyms = ', '.join(dict_response['meanings'][0]['definitions'][0]['synonyms'])
    else:
        synonyms = 'not found.'
    return synonyms


if __name__ == '__main__':
    print(time.time())
    print(translate('cold'))
    print(time.time())
    print(emoji('cold'))
    print(time.time())
    print(google_dict('word'))
    print(time.time())
    print(search_image('word'))
    print(time.time())
    print(search_synonyms('word'))
    print(time.time())
    print(1)
