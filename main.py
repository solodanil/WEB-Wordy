import os
import datetime

import requests
from flask import Flask, url_for, request, render_template, redirect, flash
from flask_login import current_user, login_user, LoginManager, logout_user, login_required
from werkzeug.exceptions import abort
from werkzeug.utils import secure_filename
from dateutil import parser
import vk_api

from data import db_session
from data.speaking_club import SpeakingClub
from data.user import User
from forms.club_form import SpeakingClubForm
from data.word_to_user import Vocabulary

from data.collection import Collection, Word
from forms.collection_form import CollectionForm, CollectionClubForm
from forms.word_form import WordForm

from tools import get_collections, get_club
import config

import dictionary

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'
login_manager = LoginManager()
login_manager.init_app(app)

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
    raw_collections = db_sess.query(Collection).all()[-2::]
    collections = get_collections(raw_collections)
    return render_template('index.html', collections=collections)


@app.route('/auth')
def login():
    return redirect(
        'https://oauth.vk.com/authorize?client_id=7827948&display=page&redirect_uri=http://127.0.0.1:8080/oauth_handler&scope=friends,email,offline&response_type=code&v=5.130')


@app.route('/oauth_handler')
def oauth_handler():
    req_url = f'https://oauth.vk.com/access_token?client_id={config.vk_id}&client_secret={config.vk_secret}&redirect_uri=http://127.0.0.1:8080/oauth_handler&code={request.args.get("code")}'
    response = requests.get(req_url).json()
    if not current_user.is_anonymous:
        return redirect(url_for('index'))
    if response['user_id'] is None:
        flash('Authentication failed.')
        return redirect(url_for('index'))
    db_sess = db_session.create_session()
    user = db_sess.query(User).filter(User.social_id == response['user_id']).first()
    if not user:
        vk_session = vk_api.VkApi(token=response['access_token'])
        vk = vk_session.get_api()
        user_obj = vk.users.get(user_id=response['user_id'], fields="contacts")[0]
        print(user_obj)
        user = User()
        user.social_id = response['user_id']
        user.name = user_obj['first_name']
        user.surname = user_obj['last_name']
        user.email = response.get('email')
        db_sess.add(user)
        db_sess.commit()
    login_user(user, True)
    return redirect(url_for('index'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")


@app.route('/clubs')
def clubs():
    db_sess = db_session.create_session()
    dates = db_sess.query(SpeakingClub.date).all()
    if not current_user.is_anonymous:
        user = db_sess.query(User).filter(User.id == current_user.id).first()
    dates.sort()
    res_clubs = {}
    for date in dates:
        date = date[0]
        raw_clubs = db_sess.query(SpeakingClub).filter(SpeakingClub.date == date).all()
        if date == datetime.date.today():
            date = 'Сегодня'
        elif date == datetime.date.today() + datetime.timedelta(days=1):
            date = 'Завтра'
        else:
            date = date.strftime('%d %B')
        raw_clubs.sort(key=lambda x: (x.date, x.time))
        res_clubs[date] = list()
        for raw_club in raw_clubs:
            club = get_club(raw_club, current_user)
            res_clubs[date].append(club)
    return render_template('clubs.html', clubs=res_clubs, title='Разговорные клубы')


@app.route('/clubs/<club_id>')
def club_page(club_id):
    db_sess = db_session.create_session()
    raw_club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()
    booked = False
    user = db_sess.query(User).filter(User.id == current_user.id).first()
    if 'unbook' in request.args:
        user.speaking_club.remove(raw_club)
        db_sess.commit()
        booked = False
    elif 'book' in request.args:
        raw_club.users.append(user)
        db_sess.commit()
        booked = True
    club = get_club(raw_club, current_user, booked=booked, from_club_page=True)
    return render_template('club_page.html', club=club, title=club['title'])


@app.route('/del_club/<club_id>')
def delete_club(club_id):
    if not current_user.is_admin:
        return abort(404)
    db_sess = db_session.create_session()
    club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()
    db_sess.delete(club)
    db_sess.commit()
    return redirect('index')


@app.route('/word/<word>')
def word(word):
    word = word.lower()
    smile = dictionary.emoji(word)
    added = False
    db_sess = db_session.create_session()
    if word == smile:
        smile = ''
    if not dictionary.google_dict(word, 'en_US'):
        abort(404)
    if current_user.is_anonymous:
        active = False
        added = False
    else:
        active = True
        vocs = db_sess.query(Vocabulary).filter(Vocabulary.user_id == current_user.id).all()
        for voc in vocs:
            if voc.word.word == word:
                added = True
        print(added)
        if 'add' in request.args and not added:
            word_obj = db_sess.query(Word).filter(Word.word == word).first()
            if not word_obj:
                word_obj = Word()
                word_obj.word = word
                db_sess.commit()
            voc = Vocabulary(user_id=current_user.id, word=word_obj)
            db_sess.add(voc)
            db_sess.commit()
            added = True
    dict_response = dictionary.google_dict(word)[0]
    return render_template('word.html', original=word.capitalize(),
                           image=dictionary.search_image(word),
                           translate_word=dictionary.translate(word),
                           emodji=smile,
                           trancription=dict_response['phonetics'][0]['text'],
                           definition=dict_response['meanings'][0]['definitions'][0]['definition'],
                           synonyms=dictionary.search_synonyms(word), added=added, active=active)


@app.route('/new_club', methods=['GET', 'POST'])
@login_required
def add_club():
    if not current_user.is_admin:
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

        os.mkdir(os.path.join(basedir, f'static/images/clubs/{club_id}'))
        img.save(os.path.join(basedir, f'static/images/clubs/{club_id}/{filename}'))
        club.image = f'static/images/clubs/{club_id}/{filename}'
        db_sess.add(club)
        db_sess.commit()
        return redirect(f'./clubs/{club_id}')
    return render_template('new_club.html', title='Добавление разговорного клуба',
                           form=form)


@app.route('/new_collection', methods=['GET', 'POST'])
@login_required
def new_collection():
    if not current_user.is_admin:
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

        os.mkdir(os.path.join(basedir, f'static/images/collection/{collection_id}'))
        img.save(os.path.join(basedir, f'static/images/collection/{collection_id}/{filename}'))
        collection.image = f'static/images/collection/{collection_id}/{filename}'
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


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
