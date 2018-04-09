import os
import pytest
from . import path

from ComposeController import ComposeController


def test__read_compose_file__pass():
    descriptor = 'dc-port.yml'
    ctl = ComposeController(base_dir=os.path.join(path, 'fixtures'))

    ctl.dispatch(['-f', descriptor, 'up', '-d'])

    ctl.dispatch(['-f', descriptor, 'down'])