import asyncio

import aiohttp

from . import app

API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'
REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'


async def upload_file_and_get_url(session, file):
    path = f'app:/{file.filename}'
    headers = {'Authorization': f'OAuth {app.config["DISK_TOKEN"]}'}

    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=headers,
        params={'path': path, 'overwrite': 'true'}
    ) as response:
        upload_url = (await response.json())['href']

    async with session.put(upload_url, data=file.read()):
        pass

    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=headers,
        params={'path': path}
    ) as response:
        return (await response.json())['href']


async def upload_files_to_disk(files):
    async with aiohttp.ClientSession(raise_for_status=True) as session:
        return await asyncio.gather(
            *(upload_file_and_get_url(session, file) for file in files)
        )
