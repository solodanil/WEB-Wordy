import datetime

import pymorphy2

from data import db_session
from data.user import User


def get_collections(raw_collections, user_words):
    collections = list()
    for collection in raw_collections:
        words = []
        added = False
        for word in collection.word:
            words.append(word.word)
        if set(words) == user_words & set(words):
            added = True
        morph = pymorphy2.MorphAnalyzer()
        slov_parse = morph.parse('слово')[0]
        slov = slov_parse.make_agree_with_number(len(words)).word
        collections.append({'name': collection.name,
                            'description': collection.description,
                            'image': ''.join(['../', str(collection.image)]),
                            'words_len': ' '.join((str(len(words)), slov)),
                            'words': words,
                            'id': collection.id,
                            'added': added})
    print(collections)
    return collections


def get_club(raw_club, current_user, user_words, booked=False, from_club_page=False):
    morph = pymorphy2.MorphAnalyzer()
    mest_parse = morph.parse('место')[0]
    min_parse = morph.parse('минута')[0]
    active = True
    free_seats = raw_club.number_of_seats - len(raw_club.users)
    mest = mest_parse.make_agree_with_number(free_seats).word
    minut = min_parse.make_agree_with_number(raw_club.duration).word
    if current_user.is_anonymous:
        active = False
    else:
        if current_user in raw_club.users:
            booked = True

    if raw_club.date < datetime.date.today():
        active = False
        booked = False
    raw_collections = raw_club.collection
    collections = get_collections(raw_collections, user_words)
    if from_club_page:
        image = ''.join(['../', str(raw_club.image)])
    else:
        image = raw_club.image
    club = {'id': raw_club.id,
            'title': raw_club.title,
            'description': raw_club.description,
            'date': raw_club.date,
            'time': raw_club.time,
            'human_date': raw_club.date.strftime('%d %B'),
            'human_time': raw_club.time.strftime('%H:%M'),
            'duration': ' '.join((str(raw_club.duration), minut)),
            'link': raw_club.link,
            'free_seats': ' '.join((str(free_seats), mest)),
            'image': image,
            'active': active,
            'booked': booked,
            'collections': collections}
    return club


def get_user_words(user):
    if not user.is_anonymous:
        db_sess = db_session.create_session()
        user_new = db_sess.query(User).filter(User.id == user.id).first()
        return set(map(lambda x: x.word.word, user_new.words))
    else:
        return {}