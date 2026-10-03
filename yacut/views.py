import random

import aiohttp
from flask import flash, redirect, render_template, url_for

from . import app, db
from .constants import (ALLOWED_CHARS, DEFAULT_SHORT_ID_LENGTH, MAX_ATTEMPTS,
                        RESERVED_URLS)
from .forms import FilesForm, URLMapForm
from .models import URLMap
from .yandex_disk import upload_files_to_disk


def get_unique_short_id(length=DEFAULT_SHORT_ID_LENGTH):
    for _ in range(MAX_ATTEMPTS):
        short_id = ''.join(random.choices(ALLOWED_CHARS, k=length))
        if not URLMap.query.filter_by(short=short_id).first():
            return short_id
    raise RuntimeError('Не удалось сгенерировать уникальный идентификатор.')


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        short_id = form.custom_id.data
        if short_id:
            if (
                URLMap.query.filter_by(short=short_id).first() is not None or
                short_id in RESERVED_URLS
            ):
                flash('Предложенный вариант короткой ссылки уже существует.')
                return render_template('url_map.html', form=form)
        else:
            short_id = get_unique_short_id()
        url_map = URLMap(
            original=form.original_link.data,
            short=short_id
        )
        db.session.add(url_map)
        db.session.commit()

        new_url = url_for(
            'redirect_from_short',
            short_id=short_id,
            _external=True
        )
        return render_template('url_map.html', form=form, new_url=new_url)

    return render_template('url_map.html', form=form)


@app.route('/files', methods=['GET', 'POST'])
async def files_view():
    form = FilesForm()
    if not form.validate_on_submit():
        return render_template('files.html', form=form)

    files = form.files.data
    try:
        download_urls = await upload_files_to_disk(files)
    except aiohttp.ClientError:
        flash('Не удалось загрузить файлы на Яндекс Диск.')
        return render_template('files.html', form=form)

    uploaded = []
    for file, download_url in zip(files, download_urls):
        short_id = get_unique_short_id()
        db.session.add(URLMap(original=download_url, short=short_id))
        uploaded.append({
            'filename': file.filename,
            'short_link': url_for(
                'redirect_from_short', short_id=short_id, _external=True
            ),
        })
    db.session.commit()

    return render_template('files.html', form=form, files=uploaded)


@app.route('/<string:short_id>')
def redirect_from_short(short_id):
    url_map = URLMap.query.filter_by(short=short_id).first_or_404()

    return redirect(url_map.original)
