import os
from string import lower

from dotenv import load_dotenv, find_dotenv


class Settings:
    def __init__(self):
        load_dotenv(find_dotenv())

        self.log_level = (os.environ.get('LOG_LEVEL') or 'DEBUG').upper()

        # Docker orchestrator
        self.docker_host = (os.environ.get('DOCKER_HOST') or 'unix://var/run/docker.sock')
        self.docker_tls_verify = (os.environ.get('DOCKER_TLS_VERIFY') or '1')
        self.docker_cert_path = (os.environ.get('DOCKER_CERT_PATH') or '')

        # Library: HTTP
        self.http_get_timeout = (os.environ.get('HTTP_GET_TIMEOUT') or '5.0')

        # Library: SuiteSetup
        self.orchestrator = lower((os.environ.get('ORCHESTRATOR')) or 'docker-compose')