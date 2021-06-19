import datetime

import pymorphy2

from data import db_session
from data.user import User
from data.speaking_club import SpeakingClub
from config import url


def get_calendar_link(raw_club):
    start_date = datetime.datetime.combine(raw_club.date, raw_club.time)
    stop_date = start_date + datetime.timedelta(minutes=raw_club.duration)
    return f'''https://calendar.google.com/calendar/r/eventedit?text={raw_club.title}&details=Перейти к встрече: {url}%2Fclubs%2F{raw_club.id}&dates={start_date.isoformat().replace("-", "").replace(":", "")}Z/{stop_date.isoformat().replace("-", "").replace(":", "")}Z'''


def get_collections(raw_collections, user_words):
    """сюреализация подборок"""
    collections = list()
    for collection in raw_collections:
        words = []
        added = False
        for word in collection.word:
            words.append(word.word)
        if set(words) == set(user_words) & set(words):
            added = True
        morph = pymorphy2.MorphAnalyzer()
        slov_parse = morph.parse('слово')[0]
        slov = slov_parse.make_agree_with_number(len(words)).word
        collections.append({'name': collection.name,
                            'description': collection.description,
                            'image': collection.image,
                            'words_len': ' '.join((str(len(words)), slov)),
                            'words': words,
                            'id': collection.id,
                            'added': added})
    return collections


def get_club(raw_club, current_user, user_words, booked=False, from_club_page=False):
    morph = pymorphy2.MorphAnalyzer()
    mest_parse = morph.parse('место')[0]
    min_parse = morph.parse('минута')[0]
    active = True
    free_seats = raw_club.number_of_seats - len(raw_club.users)  # количество оставшихся мест
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
    if free_seats == 0:
        active = False
        free_seats = 'нет'
    raw_collections = raw_club.collection
    collections = get_collections(raw_collections, user_words)
    image = raw_club.image
    calendar_link = get_calendar_link(raw_club)
    club = {'id': raw_club.id,
            'title': raw_club.title,
            'description': raw_club.description,
            'date': raw_club.date,
            'time': datetime.datetime.combine(datetime.date.today(), raw_club.time),
            'human_date': raw_club.date.strftime('%d %B'),
            'human_time': raw_club.time.strftime('%H:%M'),
            'duration': ' '.join((str(raw_club.duration), minut)),
            'link': raw_club.link,
            'free_seats': ' '.join((str(free_seats), mest)),
            'image': image,
            'active': active,
            'booked': booked,
            'collections': collections,
            'calendar_link': calendar_link}
    return club


def get_user_words(user):
    if not user.is_anonymous:
        db_sess = db_session.create_session()
        user_new = db_sess.query(User).filter(User.id == user.id).first()
        return set(map(lambda x: x.word.word, user_new.words))
    else:
        return {}
