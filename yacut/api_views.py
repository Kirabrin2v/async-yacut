from http import HTTPStatus

from flask import jsonify, request

from . import app
from .error_handlers import (InvalidAPIUsage, InvalidShortIdError,
                             ShortIdExistsError, ShortIdGenerationError)
from .models import URLMap


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    try:
        url_map = URLMap.create_from_user_query(
            url=data.get('url'),
            custom_id=data.get('custom_id')
        )
    except (InvalidShortIdError, ShortIdExistsError) as error:
        raise InvalidAPIUsage(str(error))
    except ShortIdGenerationError:
        # Текст ошибки изменён, т.к. оригинальный
        # предназначен только для разработчиков
        raise InvalidAPIUsage(
            'Не удалось сгенерировать ID. '
            'Попробуйте снова или заполните поле "custom_id"'
        )

    return jsonify(url_map.to_dict()), HTTPStatus.CREATED


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.get_from_short_id(short_id)
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', HTTPStatus.NOT_FOUND)
    return jsonify({'url': url_map.original}), HTTPStatus.OK
