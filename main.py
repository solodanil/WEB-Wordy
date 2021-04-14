import os
from os.path import dirname, realpath
import datetime

from flask import Flask, url_for, request, render_template, redirect
from werkzeug.utils import secure_filename
from dateutil import parser

from data import db_session
from data.speaking_club import SpeakingClub
from forms.club_form import SpeakingClubForm

from data.collection import Collection, Word
from forms.collection_form import CollectionForm
from forms.word_form import WordForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'

basedir = os.path.abspath(os.path.dirname(__file__))


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/clubs')
def clubs():
    db_sess = db_session.create_session()
    raw_clubs = db_sess.query(SpeakingClub).all()
    club_list = list()
    for raw_club in raw_clubs:
        club = {'id': raw_club.id,
                'title': raw_club.title,
                'description': raw_club.description,
                'date': raw_club.date,
                'time': raw_club.time,
                'human_date': raw_club.date.strftime('%m %B'),
                'human_time': raw_club.time.strftime('%H:%M'),
                'duration': raw_club.duration,
                'link': raw_club.link,
                'number_of_seats': raw_club.number_of_seats,  # нужно будет высчитывать кол-во оставшихся мест
                'image': raw_club.image,
                'active': True}
        club_list.append(club)
    club_list.sort(key=lambda x: (x['date'], x['time']))
    return render_template('clubs.html', clubs=club_list, title='Разговорные клубы')


@app.route('/clubs/<club_id>')
def club_page(club_id):
    db_sess = db_session.create_session()
    raw_club = db_sess.query(SpeakingClub).filter(SpeakingClub.id == club_id).first()
    club = {'id': raw_club.id,
            'title': raw_club.title,
            'description': raw_club.description,
            'date': raw_club.date,
            'time': raw_club.time,
            'human_date': raw_club.date.strftime('%m %B'),
            'human_time': raw_club.time.strftime('%H:%M'),
            'duration': raw_club.duration,
            'link': raw_club.link,
            'number_of_seats': raw_club.number_of_seats,  # нужно будет высчитывать кол-во оставшихся мест
            'image': ''.join(['../', raw_club.image]),
            'active': True}
    return render_template('club_page.html', club=club, title=club['title'])


@app.route('/word')
def word():
    return render_template('word.html')


@app.route('/new_club', methods=['GET', 'POST'])
def add_club():
    form = SpeakingClubForm()
    print(0)
    print(form.validate_on_submit())
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
        id = db_sess.query(SpeakingClub).order_by(SpeakingClub.id.desc()).first().id + 1

        print(f'static/images/clubs/{filename}')
        os.mkdir(os.path.join(basedir, f'static/images/clubs/{id}'))
        img.save(os.path.join(basedir, f'static/images/clubs/{id}/{filename}'))
        club.image = f'static/images/clubs/{id}/{filename}'
        db_sess.add(club)
        db_sess.commit()
        print(club)
        return redirect(f'./clubs/{id}')
    return render_template('new_club.html', title='Добавление разговорного клуба',
                           form=form)


@app.route('/new_collection', methods=['GET', 'POST'])
def add_collection():
    form = CollectionForm()
    print(0)
    print(form.validate_on_submit())
    if form.validate_on_submit():
        db_sess = db_session.create_session()
        collection = Collection()
        collection.name = form.name.data
        collection.description = form.content.data
        img = form.image.data
        filename = secure_filename(img.filename)
        id = db_sess.query(Collection).order_by(Collection.id.desc()).first().id + 1

        os.mkdir(os.path.join(basedir, f'static/images/collection/{id}'))
        img.save(os.path.join(basedir, f'static/images/collection/{id}/{filename}'))
        collection.image = f'static/images/collection/{id}/{filename}'
        db_sess.add(collection)
        db_sess.commit()
        print(collection)
        return redirect(f'/')
    return render_template('new_collection.html', title='Добавление подборки',
                           form=form)


@app.route('/add_word/<collection_id>', methods=['GET', 'POST'])
def add_word(collection_id):
    db_sess = db_session.create_session()
    collection = db_sess.query(Collection).filter(Collection.id == collection_id).first()
    print(collection)
    form = WordForm()
    if form.validate_on_submit():
        new_word = Word()
        new_word.word = form.name.data
        collection.word.append(new_word)
        db_sess.commit()
    return render_template('add_word.html', form=form, title='Добавление слова', collection_name=collection.name)


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
