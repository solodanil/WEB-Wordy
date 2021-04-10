from flask import Flask, url_for, request, render_template

from data import db_session
from data.speaking_club import SpeakingClub

app = Flask(__name__)


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


def main():
    db_session.global_init("db/database.db")
    app.run(port=8080, host='127.0.0.1')


if __name__ == '__main__':
    main()
