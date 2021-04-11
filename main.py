from flask import Flask, url_for, request, render_template, redirect

from data import db_session
from data.speaking_club import SpeakingClub
from forms.club_form import SpeakingClubForm

app = Flask(__name__)
app.config['SECRET_KEY'] = 'yandexlyceum_secret_key'


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')


@app.route('/clubs')
def clubs():
    return render_template('clubs.html')


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
        db_sess.add(club)
        db_sess.commit()
        print(club)
        return redirect('/')
    return render_template('new_club.html', title='Добавление новости',
                           form=form)


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host='127.0.0.1', debug=True)


if __name__ == '__main__':
    main()
