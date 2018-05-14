import os
# noinspection PyPackageRequirements
from dotenv import load_dotenv, find_dotenv


def set_breakpoint():
    a = Settings.respect_breakpoints
    if a is True:
        import pydevd
        pydevd.settrace('localhost', port=65000, stdoutToServer=True, stderrToServer=True)


def str2bool(val):
    return val.lower() in ("yes", "true", "t", "1")


class Settings:
    def __init__(self):
        pass

    load_dotenv(find_dotenv())
    tools = {'goss': {}}

    log_level = (os.environ.get('LOG_LEVEL') or 'DEBUG').upper()
    timing = os.environ.get('VNFROBOT_TIMING') or False
    to_console = os.environ.get('VNFROBOT_TO_CONSOLE') or False
    use_deployment = os.environ.get('VNFROBOT_USE_DEPLOYMENT') or ''
    skip_undeploy = True if use_deployment else (os.environ.get('VNFROBOT_SKIP_UNDEPLOY') or False)
    respect_breakpoints = str2bool(os.environ.get('VNFROBOT_RESPECT_BREAKPOINTS')) or False

    # Docker orchestrator
    docker = {
        'DOCKER_HOST': (os.environ.get('DOCKER_HOST') or 'unix://var/run/docker.sock'),
        # 'DOCKER_CERT_PATH': (os.environ.get('DOCKER_CERT_PATH') or ''),
        'DOCKER_TIMEOUT': (os.environ.get('DOCKER_TIMEOUT') or '2.0')
    }

    goss_helper_volume = 'goss-helper'

    # Library: HTTP
    http_get_timeout = (os.environ.get('HTTP_GET_TIMEOUT') or '0.5')
    http_max_retries = (os.environ.get('HTTP_MAX_RETRIES') or '2')
