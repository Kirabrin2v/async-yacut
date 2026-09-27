import re
import string

RESERVED_URLS = ['files']

ALLOWED_CHARS = string.ascii_letters + string.digits
DEFAULT_SHORT_ID_LENGTH = 6
MAX_SHORT_ID_LENGTH = 16
SHORT_ID_PATTERN = rf'^[{re.escape(ALLOWED_CHARS)}]+$'

MAX_ATTEMPTS = 100  # Количество попыток для генерации случайного айди
