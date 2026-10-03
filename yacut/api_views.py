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
    except InvalidShortIdError:
        raise InvalidAPIUsage('Указано недопустимое имя для короткой ссылки')
    except ShortIdExistsError:
        raise InvalidAPIUsage(
            'Предложенный вариант короткой ссылки уже существует.'
        )
    except ShortIdGenerationError:
            raise InvalidAPIUsage(
                'Не удалось сгенерировать ID. '
                'Попробуйте снова или заполните поле "custom_id"'
            )

    return url_map.to_dict()


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.get_from_short_id(short_id)
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200
