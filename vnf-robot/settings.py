import os
from string import lower

from dotenv import load_dotenv, find_dotenv


class Settings:
    def __init__(self):
        load_dotenv(find_dotenv())

        self.log_level = (os.environ.get('LOG_LEVEL') or 'DEBUG').upper()

        # Docker orchestrator
        self.docker = {'DOCKER_HOST': (os.environ.get('DOCKER_HOST') or 'unix://var/run/docker.sock'),
                       # 'DOCKER_CERT_PATH': (os.environ.get('DOCKER_CERT_PATH') or '')
                       }

        # Library: HTTP
        self.http_get_timeout = (os.environ.get('HTTP_GET_TIMEOUT') or '0.5')

        # Library: SuiteSetup
        self.orchestrator = lower((os.environ.get('ORCHESTRATOR')) or 'docker-compose')

        # Library: Socket
        self.socket_timeout = (os.environ.get('SOCKET_TIMEOUT') or '0.5')