import datetime
import os

import pymorphy2

from data import db_session
from data.user import User
from config import url


def min_agree_with_number(num: int) -> str:
    root = 'минут'
    last_digit = int(str(num)[-1])
    if last_digit == 1 and '11' not in str(num):
        return f'{root}а'
    if len(str(num)) > 1:
        last_two_digits = int(str(num)[-2:])
        if 10 <= last_two_digits <= 20:
            return f'{root}'
    if 2 <= last_digit < 5:
        return f'{root}ы'
    if 5 <= last_digit <= 9 or last_digit == 0:
        return f'{root}'
    return f'{root}'


def mest_agree_with_number(num: int) -> str:
    root = 'мест'
    last_digit = int(str(num)[-1])
    if num <= 0:
        return f'{root}'
    if last_digit == 1 and '11' not in str(num):
        return f'{root}о'
    if len(str(num)) > 1:
        last_two_digits = int(str(num)[-2:])
        if 10 <= last_two_digits <= 20:
            return f'{root}'
    if 2 <= last_digit < 5:
        return f'{root}а'
    if 5 <= last_digit <= 9 or last_digit == 0:
        return f'{root}'
    return f'{root}'


def slov_agree_with_number(num: int) -> str:
    root = 'слов'
    last_digit = int(str(num)[-1])
    if last_digit == 1 and '11' not in str(num):
        return f'{root}о'
    if len(str(num)) > 1:
        last_two_digits = int(str(num)[-2:])
        if 10 <= last_two_digits <= 20:
            return f'{root}'
    if 2 <= last_digit < 5:
        return f'{root}а'
    if 5 <= last_digit <= 9 or last_digit == 0:
        return f'{root}'
    return f'{root}'


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
        slov = slov_agree_with_number(len(words))
        collections.append({'name': collection.name,
                            'description': collection.description,
                            'image': collection.image,
                            'words_len': ' '.join((str(len(words)), slov)),
                            'words': words,
                            'id': collection.id,
                            'added': added})
    return collections


def get_club(raw_club, current_user, user_words, booked=False, from_club_page=False):
    active = True
    free_seats = raw_club.number_of_seats - len(raw_club.users)  # количество оставшихся мест
    mest = mest_agree_with_number(free_seats)
    minut = min_agree_with_number(raw_club.duration)
    if current_user.is_anonymous:
        active = False
    else:
        if current_user in raw_club.users:
            booked = True
            active = True

    if raw_club.date < datetime.date.today():
        active = False
        booked = False
    if free_seats <= 0:
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


def del_dir(dir):
    try:
        for root, dirs, files in os.walk(dir, topdown=False):
            for name in files:
                os.remove(os.path.join(root, name))
            for name in dirs:
                os.rmdir(os.path.join(root, name))
        os.rmdir(os.path.join(dir))
    except Exception:
        pass


if __name__ == '__main__':
    del_dir('not_exist')
    # morph = pymorphy2.MorphAnalyzer()
    # slov_parse = morph.parse('минута')[0]
    # for i in range(200):
    #     slov = slov_parse.make_agree_with_number(i).word
    #     if slov != min_agree_with_number(i):
    #         print(i, slov, min_agree_with_number(i))
