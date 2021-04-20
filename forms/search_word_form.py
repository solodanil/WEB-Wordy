from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired


class SearchWordForm(FlaskForm):
    text = StringField(label=('Поиск слова'), validators=[DataRequired()])
    submit = SubmitField('Найти')