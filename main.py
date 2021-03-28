from flask import Flask, url_for, request, render_template

app = Flask(__name__)


@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/clubs')
def clubs():
    return render_template('clubs.html')


if __name__ == '__main__':
    app.run(port=8080, host='127.0.0.1')