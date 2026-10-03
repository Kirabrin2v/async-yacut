import aiohttp
from flask import abort, flash, redirect, render_template, url_for

from . import app, db
from .error_handlers import (InvalidShortIdError, ShortIdExistsError,
                             ShortIdGenerationError)
from .forms import FilesForm, URLMapForm
from .models import URLMap
from .yandex_disk import upload_files_to_disk


@app.route('/', methods=['GET', 'POST'])
def index_view():
    form = URLMapForm()
    if form.validate_on_submit():
        try:
            url_map = URLMap.create_from_user_query(
                url=form.original_link.data,
                custom_id=form.custom_id.data
            )
        except InvalidShortIdError:
            flash('Указано недопустимое имя для короткой ссылки')
        except ShortIdExistsError:
            flash('Предложенный вариант короткой ссылки уже существует.')
        except ShortIdGenerationError:
            flash('Не удалось сгенерировать ID. Попробуйте снова или введите вручную')
        else:
            new_url = url_map.get_full_short_url()
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
        try:
            url_map = URLMap.create_from_user_query(url=download_url)
        except ShortIdGenerationError:
            flash('Возникла ошибка при генерации ссылки. Попробуйте ещё раз')
            return render_template('files.html', form=form)

        uploaded.append({
            'filename': file.filename,
            'short_link': url_map.get_full_short_url(),
        })
    db.session.commit()

    return render_template('files.html', form=form, files=uploaded)


@app.route('/<string:short_id>')
def redirect_from_short(short_id):
    url_map = URLMap.get_from_short_id(short_id)
    if url_map is None:
        abort(404)

    return redirect(url_map.original)
