from flask_wtf import FlaskForm
from flask_wtf.file import FileRequired, MultipleFileField
from wtforms import StringField, SubmitField, URLField
from wtforms.validators import DataRequired, Length, Optional, Regexp

from .constants import MAX_SHORT_ID_LENGTH, SHORT_ID_PATTERN


class URLMapForm(FlaskForm):
    original_link = URLField(
        'Длинная ссылка',
        validators=[DataRequired(message='Обязательное поле')]
    )
    custom_id = StringField(
        'Ваш вариант короткой ссылки',
        validators=[
            Optional(),
            Length(1, MAX_SHORT_ID_LENGTH),
            Regexp(
                SHORT_ID_PATTERN,
                message='Допустимы только латинские буквы и цифры'
            )
        ]
    )

    submit = SubmitField('Создать')


class FilesForm(FlaskForm):
    files = MultipleFileField(
        'Выберите файлы',
        validators=[FileRequired(message='Выберите хотя бы один файл')]
    )
    submit = SubmitField('Загрузить')
