import requests
import json

import translators as ts
from emoji_translate import Translator


def google_dict(word, lang='en_US'):
    response = requests.get(f'https://api.dictionaryapi.dev/api/v2/entries/{lang}/{word}').json()
    if 'title' in response:
        return False
    else:
        return response


def translate(word, lang='ru'):
    return ts.google(word, to_language=lang)


def emoji(word):
    emo = Translator(exact_match_only=False)
    return emo.emojify(word)


def search_image(word):
    response = requests.get(
        f'https://api.unsplash.com/search/photos?page=1&query={word}&client_id=LbDsTQQY_mSADos2tEp_Y_JXtseb7l92LtH0J0Z1KjY').json()
    image = response['results'][0]['urls']['raw']
    return image


def search_synonyms(word):
    if 'synonyms' in google_dict(word)[0]['meanings'][0]['definitions'][0]:
        synonyms = ', '.join(google_dict(word)[0]['meanings'][0]['definitions'][0]['synonyms'])
    else:
        synonyms = 'not found.'
    return synonyms


if __name__ == '__main__':
    print(translate('cold'))
    print(emoji('cold'))
