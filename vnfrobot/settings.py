import os
# noinspection PyPackageRequirements
from dotenv import load_dotenv, find_dotenv


def set_breakpoint():
    """
    Helper method to set a PyCharm breakpoint in case a remote debugger is running. If it is called somewhere with no
    remote debugger connected, the program will wait for the debugger. And wait. And wait...

    Returns:
        None

    """
    a = Settings.respect_breakpoints
    if a is True:
        import pydevd
        pydevd.settrace('localhost', port=65000, stdoutToServer=True, stderrToServer=True)


def str2bool(val):
    """
    Converts a string to a boolean

    Args:
        val: str

    Returns:
        boolean

    """
    return val.lower() in ("yes", "true", "t", "1")


class Settings:
    """
    Settings class. It looks in the environment variables and in a .env file for settings that are applied to the
    VnfValidator globally.

    Useful default values are used if no settings are found.
    """
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
