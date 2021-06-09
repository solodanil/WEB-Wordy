from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class WordForm(FlaskForm):
    name = StringField('Слово', validators=[DataRequired()])
    submit = SubmitField('Создать')