import random
import re
from datetime import datetime

from flask import jsonify, url_for

from . import db
from .constants import (ALLOWED_CHARS, DEFAULT_SHORT_ID_LENGTH, MAX_ATTEMPTS,
                        MAX_SHORT_ID_LENGTH, RESERVED_URLS, SHORT_ID_PATTERN)
from .error_handlers import (InvalidShortIdError, ShortIdExistsError,
                             ShortIdGenerationError)


class URLMap(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    original = db.Column(db.String, nullable=False)
    short = db.Column(db.String(MAX_SHORT_ID_LENGTH), nullable=False, unique=True)
    timestamp = db.Column(db.DateTime, index=True, default=datetime.utcnow)

    @classmethod
    def create_from_user_query(cls, url, custom_id=None):
        if custom_id:
            if (
                not isinstance(custom_id, str) or
                len(custom_id) > MAX_SHORT_ID_LENGTH or
                not re.fullmatch(SHORT_ID_PATTERN, custom_id)
            ):
                raise InvalidShortIdError(
                    f'ID не соответствует шаблону: {custom_id}'
                )
            if (
                custom_id in RESERVED_URLS or
                cls.get_from_short_id(custom_id) is not None
            ):
                raise ShortIdExistsError(f'ID уже существует: {custom_id}')
        else:
            custom_id = cls.get_unique_short_id()

        url_map = cls(original=url, short=custom_id)
        db.session.add(url_map)
        db.session.commit()

        return url_map

    @classmethod
    def get_from_short_id(cls, short_id):
        return cls.query.filter_by(short=short_id).first()

    def get_full_short_url(self):
        return url_for(
            'redirect_from_short',
            short_id=self.short,
            _external=True
        )

    @staticmethod
    def get_unique_short_id(length=DEFAULT_SHORT_ID_LENGTH):
        for _ in range(MAX_ATTEMPTS):
            short_id = ''.join(random.choices(ALLOWED_CHARS, k=length))
            if not URLMap.query.filter_by(short=short_id).first():
                return short_id
        raise ShortIdGenerationError(
            f'Возможно, все уникальные значения для ID с длиной {length}'
            'закончились. Попробуйте увеличить length.'
        )

    def to_dict(self):
        return jsonify({
            'url': self.original,
            'short_link': self.get_full_short_url(),
        }), 201