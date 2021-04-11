from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class SpeakingClubForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Описание")
    date = StringField('Дата')
    submit = SubmitField('Создать')