import os
from os.path import dirname, realpath
import datetime

from flask import Flask, url_for, request, render_template, redirect
from werkzeug.utils import secure_filename
from dateutil import parser

from data import db_session
from data.speaking_club import SpeakingClub
from forms.club_form import SpeakingClubForm

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
                'date': raw_club.date, # нужно будет сделать нормальный формат
                'time': raw_club.time,
                'duration': raw_club.duration,
                'link': raw_club.link,
                'number_of_seats': raw_club.number_of_seats, # нужно будет высчитывать кол-во оставшихся мест
                'image': raw_club.image,
                'active': True}
        club_list.append(club)
    return render_template('clubs.html', clubs=club_list)


@app.route('/clubs/0')
def club_page():
    return render_template('club_page.html')


@app.route('/word')
def word():
    return render_template('word.html')


@app.route('/new_club', methods=['GET', 'POST'])
def add_news():
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
        club.image = os.path.join(basedir, f'static/images/clubs/{id}/{filename}')
        db_sess.add(club)
        db_sess.commit()
        print(club)
        return redirect(f'./club/{id}')
    return render_template('new_club.html', title='Добавление новости',
                           form=form)


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
