import os
from . import path

from ComposeController import ComposeController


def test__read_compose_file__pass():
    descriptor = 'dc-test.yml'
    ctl = ComposeController(base_dir=os.path.join(path, 'fixtures'))

    ctl._dispatch(['-f', descriptor, 'up', '-d'])

    ctl._dispatch(['-f', descriptor, 'down'])