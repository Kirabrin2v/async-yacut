import re

from flask import jsonify, request, url_for

from . import app, db
from .constants import MAX_SHORT_ID_LENGTH, RESERVED_URLS, SHORT_ID_PATTERN
from .error_handlers import InvalidAPIUsage
from .models import URLMap
from .views import get_unique_short_id


@app.route('/api/id/', methods=['POST'])
def create_id():
    data = request.get_json(silent=True)
    if not data or not isinstance(data, dict):
        raise InvalidAPIUsage('Отсутствует тело запроса')
    if 'url' not in data:
        raise InvalidAPIUsage('"url" является обязательным полем!')

    custom_id = data.get('custom_id')
    if custom_id:
        if (
            not isinstance(custom_id, str) or
            len(custom_id) > MAX_SHORT_ID_LENGTH or
            not re.fullmatch(SHORT_ID_PATTERN, custom_id)
        ):
            raise InvalidAPIUsage(
                'Указано недопустимое имя для короткой ссылки'
            )
        if (
            custom_id in RESERVED_URLS or
            URLMap.query.filter_by(short=custom_id).first() is not None
        ):
            raise InvalidAPIUsage(
                'Предложенный вариант короткой ссылки уже существует.'
            )
    else:
        custom_id = get_unique_short_id()

    url_map = URLMap(original=data['url'], short=custom_id)
    db.session.add(url_map)
    db.session.commit()

    return jsonify({
        'url': url_map.original,
        'short_link': url_for(
            'redirect_from_short',
            short_id=url_map.short,
            _external=True
        ),
    }), 201


@app.route('/api/id/<string:short_id>/', methods=['GET'])
def get_url(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first()
    if url_map is None:
        raise InvalidAPIUsage('Указанный id не найден', 404)
    return jsonify({'url': url_map.original}), 200
