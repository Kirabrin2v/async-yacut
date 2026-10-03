# YaCut

YaCut - это сервис укорачивания ссылок. Он связывает длинную ссылку с короткой, которую предлагает сам пользователь или генерирует сервис. Кроме того, YaCut умеет загружать файлы на Яндекс Диск и выдавать короткие ссылки для их скачивания.

## Описание проекта

**YaCut** - это приложение, позволяющее пользователям:

- получать короткую ссылку для любого адреса;
- предлагать собственный вариант короткой ссылки (до 16 символов, латинские буквы и цифры);
- загружать сразу несколько файлов на Яндекс Диск и получать короткую ссылку на скачивание каждого из них;
- работать с сервисом через REST API.

Если пользователь не указал свой вариант, сервис генерирует идентификатор из шести случайных символов и проверяет, что он ещё не занят.

## Функциональность

- Создание коротких ссылок через веб-интерфейс и API.
- Переадресация на исходный адрес при переходе по короткой ссылке.
- Асинхронная загрузка файлов на Яндекс Диск через aiohttp.
- История загруженных файлов в рамках сессии пользователя.
- Проверка пользовательских вариантов ссылок: формат, длина, занятость, зарезервированные адреса (`files`).
- Обработка ошибок отдельно для веб-интерфейса (HTML-страницы) и для API (JSON).

## Стек технологий

**Backend:**
- Python 3.12
- Flask
- Flask-SQLAlchemy
- Flask-WTF
- aiohttp
- SQLite

**Frontend:**
- Jinja2
- Bootstrap

**Тестирование:**
- Pytest
- pytest-aiohttp
- Flake8

## Структура проекта

```
yacut/
├── yacut/                  # Пакет приложения
│   ├── static/             # Статика (CSS, изображения)
│   ├── templates/          # Шаблоны страниц
│   ├── __init__.py         # Создание приложения и подключение БД
│   ├── api_views.py        # Эндпоинты API
│   ├── constants.py        # Константы проекта
│   ├── error_handlers.py   # Обработчики ошибок
│   ├── forms.py            # Формы главной страницы и загрузки файлов
│   ├── models.py           # Модель URLMap
│   ├── views.py            # View-функции веб-интерфейса
│   └── yandex_disk.py      # Работа с API Яндекс Диска
├── tests/                  # Тесты (pytest)
├── postman_collection/     # Коллекция запросов для Postman
├── openapi.yml             # Спецификация API
├── settings.py             # Конфигурация Flask
├── requirements.txt
└── README.md
```

## Развёртывание проекта

### Предварительные требования

- Python 3.12;
- Git;
- OAuth-токен Яндекс Диска.

### Локальный запуск

1. Клонируйте репозиторий и перейдите в него:

   ```bash
   git clone https://github.com/Kirabrin2v/async-yacut.git
   cd async-yacut
   ```

2. Создайте и активируйте виртуальное окружение:

   ```bash
   python3.12 -m venv venv
   source venv/bin/activate
   ```

3. Установите зависимости:

   ```bash
   pip install -r requirements.txt
   ```

4. Создайте файл `.env` в корне проекта (см. раздел [Переменные окружения](#переменные-окружения)).

5. Создайте таблицы в базе данных:

   ```bash
   flask db upgrade
   ```

6. Запустите сервер:

   ```bash
   flask run
   ```

7. Проект будет доступен по адресу:

   ```
   http://127.0.0.1:5000
   ```

   Страница загрузки файлов:

   ```
   http://127.0.0.1:5000/files
   ```

### Запуск тестов

```bash
pytest
```

## Переменные окружения

Файл `.env` должен находиться в корне проекта и содержать следующие переменные:

```env
FLASK_APP=yacut
FLASK_DEBUG=1
DATABASE_URI=sqlite:///db.sqlite3
SECRET_KEY=SECRETKEY
DISK_TOKEN=your_token
```

## Примеры запросов к API

Полная спецификация описана в файле `openapi.yml`. Его удобно открыть в [Swagger Editor](https://editor.swagger.io/). Ниже несколько примеров:

**Создание короткой ссылки:**

```
POST /api/id/
Content-Type: application/json

{
  "url": "https://practicum.yandex.ru/learn/backend-developer/courses/1fac0dd1-5f17-4c79-8c6f-272db6d092f2/sprints/790761/topics/9df972bf-def3-4a01-bf3f-25330affbb29/lessons/cd62d201-5840-4f3b-9a56-43ba30141768/",
  "custom_id": "lesson"
}
```

Ответ `201 Created`:

```json
{
  "url": "https://practicum.yandex.ru/learn/backend-developer/courses/1fac0dd1-5f17-4c79-8c6f-272db6d092f2/sprints/790761/topics/9df972bf-def3-4a01-bf3f-25330affbb29/lessons/cd62d201-5840-4f3b-9a56-43ba30141768/",
  "short_link": "http://127.0.0.1:5000/lesson"
}
```

Поле `custom_id` необязательное. Если его не передать, идентификатор будет сгенерирован автоматически.

**Получение исходной ссылки по короткому идентификатору:**

```
GET /api/id/lesson/
```

Ответ `200 OK`:

```json
{
  "url": "https://practicum.yandex.ru/learn/backend-developer/courses/1fac0dd1-5f17-4c79-8c6f-272db6d092f2/sprints/790761/topics/9df972bf-def3-4a01-bf3f-25330affbb29/lessons/cd62d201-5840-4f3b-9a56-43ba30141768/"
}
```

**Пример ошибки:**

```
POST /api/id/
Content-Type: application/json

{
  "url": "https://example.com",
  "custom_id": "lesson"
}
```

Ответ `400 Bad Request`:

```json
{
  "message": "Предложенный вариант короткой ссылки уже существует."
}
```

## Автор

**Kirabrin** ([Гитхаб](https://github.com/Kirabrin2v))
