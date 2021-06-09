from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class SpeakingClubForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Описание")
    date = StringField('Дата')
    time = StringField('Время')
    duration = StringField('Продолжительность (в минутах)')
    link = StringField('Ссылка')
    number_of_seats = StringField('Количество мест')
    image = FileField('Обложка')
    submit = SubmitField('Создать')