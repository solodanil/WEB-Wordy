from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, FileField
from wtforms import BooleanField, SubmitField
from wtforms.validators import DataRequired


class CollectionForm(FlaskForm):
    name = StringField('Название', validators=[DataRequired()])
    content = TextAreaField("Описание")
    image = FileField('Обложка')
    submit = SubmitField('Создать')