import logging
import os
import datetime
import shutil
import os.path as op

import requests
from flask import Flask, url_for, request, render_template, redirect, flash, make_response, send_from_directory
from flask_admin import Admin
from flask_admin.contrib.fileadmin import FileAdmin
from flask_login import current_user, login_user, LoginManager, logout_user, login_required
from vk_api.utils import get_random_id
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from dateutil import parser
import vk_api
from flask_restful import abort, Api
from flask_sqlalchemy import SQLAlchemy
from flask_moment import Moment
from waitress import serve

from admin import MainView, UserView, FileView, ClubView, CollectionView, VocabularyView, AccessLevelView

from data import db_session
from data.speaking_club import SpeakingClub
from data.user import User, AccessLevel
from forms.club_form import SpeakingClubForm, MailingForm
from data.word_to_user import Vocabulary

from data.collection import Collection, Word
from forms.collection_form import CollectionForm, CollectionClubForm
from forms.word_form import WordForm

import resources

from tools import get_collections, get_club, get_user_words, del_dir
import config

import dictionary

werkzeug_logger = logging.getLogger('werkzeug')
werkzeug_logger.setLevel(logging.INFO)
logging.basicConfig(level=logging.INFO, format='%(asctime)s %(levelname)s:%(name)s:%(message)s')
logging.basicConfig(
    level="DEBUG",
    format="%(asctime)s %(levelname)s:%(name)s:%(message)s",
    datefmt='%d-%b-%y %H:%M:%S',
    force=True,
    handlers=[
        logging.FileHandler("debug.log"),
        logging.StreamHandler()
    ])
logging.info('This is app launching')

app = Flask(__name__)
api = Api(app)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

moment = Moment(app)

app.config['DATABASE_FILE'] = "db/database.db"
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{app.config["DATABASE_FILE"]}?check_same_thread=False'
app.config['SQLALCHEMY_ECHO'] = True
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

admin = Admin(app)
db = SQLAlchemy(app)
admin.add_view(UserView(User, db.session))
admin.add_view(ClubView(SpeakingClub, db.session))
admin.add_view(CollectionView(Collection, db.session))
admin.add_view(VocabularyView(Vocabulary, db.session))
admin.add_view(VocabularyView(Word, db.session))
admin.add_view(AccessLevelView(AccessLevel, db.session))
path = op.join(op.dirname(__file__), 'static')
admin.add_view(FileView(path, '/static/', name='Static Files'))

basedir = os.path.abspath(os.path.dirname(__file__))


@login_manager.user_loader
def load_user(user_id):
    db_sess = db_session.create_session()
    return db_sess.query(User).get(user_id)


@app.errorhandler(404)
def not_found(error):
    return render_template('404_error.html')


@app.route('/')
@app.route('/index')
def index():
    db_sess = db_session.create_session()
    user_words = get_user_words(current_user)  # получаем слова, которые пользователь добавил в словарь
    raw_collections = db_sess.query(Collection).all()[-2::]  # получаем две самых новых подборки слов
    collections = get_collections(raw_collections, user_words)  # переводим подборки в нужный формат
    res = list()
    soonest = db_sess.query(SpeakingClub).filter(SpeakingClub.date >= datetime.date.today()).order_by(
        SpeakingClub.date).all()[:3]  # получаем три ближайших клуба
    soonest = list(map(lambda club: ('БЛИЖАЙШИЙ', club), soonest))
    few_seats = db_sess.query(SpeakingClub).filter(SpeakingClub.date > datetime.date.today()).all()
    few_seats = sorted(few_seats, key=lambda x: x.number_of_seats - len(x.users))[
        0]  # получаем клуб с наименьшим кол-вом свободных мест
    new_collection_show = False
    if not current_user.is_anonymous:  # ищем ближайший клуб, на который записан пользователь
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not user.access_level.index:
            return 'Отказано в доступе. Обратитесь в поддержку'
        new_collection_show = user.access_level.new_collection
        user_clubs = user.speaking_club
        user_clubs = list(filter(lambda club: club.date >= datetime.date.today(), user_clubs))
        if user_clubs:
            res.append(('ВЫ ЗАПИСАНЫ', sorted(user_clubs, key=lambda club: (club.date, club.time))[0]))
    res += soonest
    res.append(tuple())
    res[2] = ('ОСТАЛОСЬ МАЛО МЕСТ', few_seats)
    user_words = get_user_words(current_user)
    res = list(map(lambda x: (x[0], get_club(x[1], current_user, user_words)), res[:3]))
    print(res)
    return render_template('index.html', collections=collections, clubs=res, title='Wordy',
                           new_collection_show=new_collection_show)


@app.route('/auth')
def login():
    """Перенаправляет пользователя на авторизацию ВК и запоминает в куки предыдущую страницу"""
    res = make_response(redirect(
        f'https://oauth.vk.com/authorize?client_id={config.vk_id}&display=page&redirect_uri=http://{request.headers.get("host")}/oauth_handler&scope=friends,email,offline&response_type=code&v=5.130'))
    print(request.headers.get('Referer'))
    res.set_cookie('auth_redirect', request.headers.get('Referer'), max_age=60 * 20)
    return res


@app.route('/oauth_handler')
def oauth_handler():
    """обрабатывает ответ oauth, регистрирует или авторизует пользователя, после чего возвращает на страницу из куки"""
    req_url = f'https://oauth.vk.com/access_token?client_id={config.vk_id}&client_secret={config.vk_secret}&redirect_uri=http://{request.headers.get("host")}/oauth_handler&code={request.args.get("code")}'
    response = requests.get(req_url).json()
    redirect_url = request.cookies.get("auth_redirect", request.headers.get("host"))
    logging.debug(response)
    if not current_user.is_anonymous:
        logging.debug(f'not current_user.is_anonymous {response}')
        return redirect(url_for('index'))
    if response.get('user_id') is None:
        logging.debug(f'user_id is none {response}')
        print(response)
        flash('Authentication failed.')
        return redirect(url_for('index'))
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(
        User.social_id == response['user_id']).first()  # ищем пользователя с таким же social_id
    logging.debug(f"{user}, {response['user_id']}")
    if not user:  # если не находим, то создаем нового
        logging.debug(f'not user {user} {response["user_id"]} {response}')
        vk_session = vk_api.VkApi(token=response['access_token'])
        vk = vk_session.get_api()
        user_obj = vk.users.get(user_id=response['user_id'], fields="contacts")[0]
        print(user_obj)
        user = User()
        user.social_id = response['user_id']
        user.name = user_obj['first_name']
        user.surname = user_obj['last_name']
        user.email = response.get('email')
        user.access_level = db_sess.query(AccessLevel).get(1)
        db_sess.add(user)
        db_sess.commit()
        login_user(user, True)
        logging.debug(f'{user} {response} logged in')
        return redirect(redirect_url + '#notification')
    login_user(user, True)
    logging.debug(f'{user} {response} logged in')
    return redirect(redirect_url)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(f'/')


@app.route('/clubs')
def clubs():
    db_sess = db_session.create_session()
    dates = db_sess.query(SpeakingClub.date).all()  # получаем даты, в которых проходят клубы
    show_new_club_link = False
    if not current_user.is_anonymous:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
        if not user.access_level.index:
            return 'Отказано в доступе. Обратитесь в поддержку'
        show_new_club_link = db_sess.query(User).get(current_user.id).access_level.new_club
    dates.sort()
    res_clubs = {}
    for date in dates:
        date = date[0]
        raw_clubs = db_sess.query(SpeakingClub).filter(SpeakingClub.date == date).all()  # получаем клубы в нужную дату
        raw_clubs.sort(key=lambda x: (x.date, x.time))  # сортируем по дате и времени
        res_clubs[date] = list()
        for raw_club in raw_clubs:
            user_words = get_user_words(current_user)
            club = get_club(raw_club, current_user, user_words)
            res_clubs[date].append(club)
    return render_template('clubs.html', clubs=res_clubs, title='Разговорные клубы',
                           show_new_club_link=show_new_club_link)


@app.route('/clubs/<club_id>/')
def club_page(club_id):
    if club_id == 'service-worker.js':
        return abort(404)
    db_sess = db_session.create_session()
    raw_club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()  # получаем информацию о клубе
    booked = False
    if not current_user.is_anonymous:
        user = db_sess.query(User).filter(User.id == current_user.id).first()  # получаем текущего пользователя
        if not user.access_level.index:
            return 'Отказано в доступе. Обратитесь в поддержку'
    if 'unbook' in request.args:  # отмена записи
        try:
            user.speaking_club.remove(raw_club)
            db_sess.commit()
            booked = False
        except ValueError:
            pass
    elif 'book' in request.args:  # запись на клуб
        if not user.access_level.club_booking:
            return 'Отказано в доступе. Обратитесь в поддержку'
        raw_club.users.append(user)
        db_sess.commit()
        booked = True
        vk_session = vk_api.VkApi(token=config.TOKEN)
        vk = vk_session.get_api()
        try:
            vk.messages.send(
                message=f'Новая запись на клуб {user}  '
                        f' https://vk.com/gim204114880?sel={user.social_id}',
                random_id=get_random_id(),
                peer_id=281317152
            )
            vk.messages.send(
                message=f'Здравствуйте! Мы получили Вашу заявку на запись на разговорный клуб. Скоро мы отправим Вам ссылку на оплату. Однако уже сейчас можно учить слова, для этого добавьте подбору в свой словарь на сайте и напишите сюда «Начать»',
                random_id=get_random_id(),
                peer_id=user.social_id
            )
            logging.info(f'Message sent to {user}')
        except Exception as ex:
            logging.info(f'Message wasn’t sent to {user} (error {ex.__str__(), ex.args})')
    user_words = get_user_words(
        current_user)  # получаем словарь пользователя, чтобы определить, добавлял ли пользователь подборки
    club = get_club(raw_club, current_user, user_words, booked=booked, from_club_page=True)
    return render_template('club_page.html', club=club, title=club['title'])


@app.route('/clubs/<club_id>/join')
@login_required
def join_club(club_id):
    db_sess = db_session.create_session()
    raw_club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()  # получаем информацию о клубе
    if raw_club.link:
        return redirect(raw_club.link)
    else:
        return render_template('no_link.html')


@app.route('/collection/<collection_id>')
@login_required
def collection(collection_id):
    """Добавление слов из подборки в словарь пользователя"""
    db_sess = db_session.create_session()
    coll = db_sess.query(Collection).filter(Collection.id == collection_id).first()
    user = db_sess.query(User).get(current_user.id)
    if not user.access_level.words_learning:
        return 'Отказано в доступе. Обратитесь в поддержку'
    for word_obj in coll.word:
        print(word_obj)
        if not db_sess.query(Vocabulary).filter(Vocabulary.user_id == current_user.id,
                                                Vocabulary.word == word_obj).first():
            voc = Vocabulary(user_id=current_user.id, word=word_obj)
            db_sess.add(voc)
            print(f'{word_obj} was added')
        else:
            print(f'{word_obj} already added')
    print(request.referrer)
    db_sess.commit()
    return redirect(request.referrer)


@app.route('/collection/<collection_id>/delete')
@login_required
def collection_delete(collection_id):
    """Удаление подборки из словаря"""
    db_sess = db_session.create_session()
    coll = db_sess.query(Collection).filter(Collection.id == collection_id).first()
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    for word_obj in coll.word:
        voc = db_sess.query(Vocabulary).filter(Vocabulary.word == word_obj, Vocabulary.user == current_user).first()
        db_sess.delete(voc)
        # print(user.words)
        # print(word_obj)
        # user.words.remove(word_obj)
        print(voc, 'deleted')
    print(request.referrer)
    db_sess.commit()
    return redirect(request.referrer)


@app.route('/del_club/<club_id>')
def delete_club(club_id):
    """Полное удаление разговорного клуба (админами)"""
    if not current_user.is_admin:
        return abort(404)
    db_sess = db_session.create_session()
    club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()
    db_sess.delete(club)
    db_sess.commit()
    shutil.rmtree(os.path.join(basedir, f'static/images/clubs/{club_id}'))
    return redirect('index')


@app.route('/word')
def word():
    word = request.args.get('word').lower()
    print(word)
    smile = dictionary.emoji(word)  # получаем эмодзи по слову
    added = False
    db_sess = db_session.create_session()
    word_obj = db_sess.query(Word).filter(Word.word == word).first()
    if not word_obj:
        word_obj = Word()
        word_obj.word = word
        word_obj.emoji = smile
        word_obj.translation = dictionary.translate(word)
        dict_response = dictionary.google_dict(word)[0]
        if not dict_response:
            abort(404)
        word_obj.definition = dict_response['meanings'][0]['definitions'][0]['definition']
        word_obj.image_url = dictionary.search_image(word)
        word_obj.phonetic = dict_response['phonetics'][0]['text']
        db_sess.add(word_obj)
        db_sess.commit()
    if current_user.is_anonymous:
        active = False  # возможность добавить в словарь
        added = False
    else:
        active = True
        vocs = db_sess.query(Vocabulary).filter(Vocabulary.user_id == current_user.id).all()
        for voc in vocs:
            if voc.word.word == word:
                added = True
        if 'del' in request.args and added:
            voc = db_sess.query(Vocabulary).filter(Vocabulary.user_id == current_user.id,
                                                   Vocabulary.word == word_obj).first()
            db_sess.delete(voc)
            db_sess.commit()
            added = False
        elif 'add' in request.args and not added:
            user = db_sess.query(User).get(current_user.id)
            if not user.access_level.words_learning:
                return 'Отказано в доступе. Обратитесь в поддержку'
            voc = Vocabulary(user_id=current_user.id, word=word_obj)
            db_sess.add(voc)
            db_sess.commit()
            added = True
    # synonyms = dictionary.search_synonyms(dict_response)
    return render_template('word.html', original=word.capitalize(),
                           image=word_obj.image_url,
                           translate_word=word_obj.translation,
                           emodji=word_obj.emoji,
                           trancription=word_obj.phonetic,
                           definition=word_obj.definition,
                           added=added, active=active, title=word.capitalize())


@app.route('/new_club', methods=['GET', 'POST'])
@login_required
def add_club():
    if not current_user.access_level.new_club:
        return abort(404)
    form = SpeakingClubForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        club = SpeakingClub()
        club.title = form.name.data
        club.description = form.content.data
        club.date = parser.parse(form.date.data).date()
        club.time = parser.parse(form.time.data).time()
        club.duration = form.duration.data
        club.link = form.link.data
        club.number_of_seats = form.number_of_seats.data
        img = form.image.data
        filename = secure_filename(img.filename)
        try:
            club_id = db_sess.query(SpeakingClub).order_by(SpeakingClub.id.desc()).first().id + 1
        except AttributeError:
            club_id = 1
        del_dir(f'static/images/clubs/{club_id}')
        os.mkdir(os.path.join(basedir, f'static/images/clubs/{club_id}'))
        img.save(os.path.join(basedir, f'static/images/clubs/{club_id}/{filename}'))
        club.image = f'images/clubs/{club_id}/{filename}'
        db_sess.add(club)
        db_sess.commit()
        return redirect(f'./clubs/{club_id}')
    return render_template('new_club.html', title='Добавление разговорного клуба',
                           form=form)


@app.route('/new_collection', methods=['GET', 'POST'])
@login_required
def new_collection():
    if not current_user.access_level.new_collection:
        return abort(404)
    form = CollectionForm()
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        collection = Collection()
        collection.name = form.name.data
        collection.description = form.content.data
        img = form.image.data
        filename = secure_filename(img.filename)
        try:
            collection_id = db_sess.query(Collection).order_by(Collection.id.desc()).first().id + 1
        except AttributeError:
            collection_id = 1

        del_dir(f'static/images/collection/{collection_id}')
        os.mkdir(os.path.join(basedir, f'static/images/collection/{collection_id}'))
        img.save(os.path.join(basedir, f'static/images/collection/{collection_id}/{filename}'))
        collection.image = f'images/collection/{collection_id}/{filename}'
        db_sess.add(collection)
        db_sess.commit()
        return redirect(f'../add_word/{collection_id}')
    return render_template('new_collection.html', title='Добавление подборки',
                           form=form)


@app.route('/add_word/<collection_id>', methods=['GET', 'POST'])
@login_required
def add_word(collection_id):
    if not current_user.is_admin:
        return abort(404)
    db_sess = db_session.create_session()
    collection = db_sess.query(Collection).filter(Collection.id == collection_id).first()
    form = WordForm()
    if form.validate_on_submit():
        new_word = Word()
        new_word.word = form.name.data.lower()
        collection.word.append(new_word)
        db_sess.commit()
        return redirect(f'/add_word/{collection_id}')
    return render_template('add_word.html', form=form, title='Добавление слова', collection_name=collection.name)


@app.route('/clubs/<club_id>/add_collection', methods=['GET', 'POST'])
@login_required
def add_collection(club_id):
    if not current_user.is_admin:
        return abort(404)
    db_sess = db_session.create_session()
    club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()
    form = CollectionClubForm()
    if form.validate_on_submit():
        collection = db_sess.query(Collection).filter(Collection.id == form.id.data).first()
        club.collection.append(collection)
        db_sess.commit()
        return redirect(f'/clubs/{club_id}')
    return render_template('collection_club_form.html', form=form, title='Добавление подборки к клубу',
                           club_name=club.title)


@app.route('/clubs/<club_id>/mailing', methods=['GET', 'POST'])
@login_required
def club_mailing(club_id):
    # if not current_user.is_admin:
    #     return abort(404)
    db_sess = db_session.create_session()
    club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()
    form = MailingForm()
    if form.validate_on_submit():
        vk_session = vk_api.VkApi(token=config.TOKEN)
        vk = vk_session.get_api()
        for user in club.users:
            try:
                vk.messages.send(
                    message=form.text.data,
                    random_id=get_random_id(),
                    peer_id=user.social_id
                )
                logging.info(f'Message sent to {user}')
            except Exception as ex:
                logging.info(f'Message wasn’t sent to {user} (error {ex.__str__(), ex.args})')
        return redirect(f'/clubs/{club_id}')
    return render_template('mailing.html', form=form, title='Отправка сообщения',
                           club_name=club.title)


@app.route('/start')
def landing():
    return redirect('https://wordy-start.tilda.ws')


@app.route('/manifest.json')
def manifest():
    return open('manifest.json').read()


@app.route('/service-worker.js')
def sw():
    return app.send_static_file('service-worker.js')


@app.route('/offline.html')
def offline():
    return render_template('offline.html')


def main():
    db_session.global_init("db/database.db")
    api.add_resource(resources.UserResource, '/api/v1/user/<int:social_id>')
    api.add_resource(resources.VocabularyResource, '/api/v1/vocabulary/<int:user_social_id>')
    # app.run(port=8080, host='127.0.0.1', debug=True)
    serve(app, host='0.0.0.0', port=5000)


if __name__ == '__main__':
    main()
