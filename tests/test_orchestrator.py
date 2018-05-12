from tempfile import NamedTemporaryFile

import pytest
from pytest import fixture

from exc import SetupError
from tools import orchestrator
from tools.orchestrator import DockerOrchestrator


@fixture
def yaml_valid():
    return """version: "3.2"
    """


@fixture
def yaml_invalid():
    return """version= 3.2"
    """


def test___check_valid_yaml__pass(o, yaml_valid):
    with NamedTemporaryFile(mode='w+') as f:
        f.write(yaml_valid)
        f.seek(0)
        o._check_valid_yaml(f.name)


def test___check_valid_yaml__fail(o, yaml_invalid):
    with pytest.raises(SetupError):
        with NamedTemporaryFile(mode='w+') as f:
            f.write(yaml_invalid)
            f.seek(0)
            o._check_valid_yaml(f.name)
