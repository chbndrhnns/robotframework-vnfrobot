import os
from dotenv import load_dotenv, find_dotenv

load_dotenv(find_dotenv())

log_level = (os.environ.get('LOG_LEVEL') or 'DEBUG').upper()
http_get_timeout = (os.environ.get('HTTP_GET_TIMEOUT') or '5.0')
