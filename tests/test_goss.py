import os
import pytest

from exc import TestToolError
from tests.test_DockerController import _cleanup
from tools.goss import GossTool


def test__run__pass(controller, stack, service_id, gossfile, containers):
    stack_name = stack[0]

    controller.put_file(containers[0].id, gossfile)
    g = GossTool(controller, containers[0], gossfile=os.path.basename(gossfile))
    res = g.run_goss()

    assert res['summary']['failed-count'] == 1


def test__run__gossfile_not_found__fail(controller, stack, service_id, containers):
    g = GossTool(controller, containers[0])
    g.gossfile = 'bla'

    with pytest.raises(TestToolError, match='Gossfile not found'):
        g.run_goss()


def test__run__goss_not_found__fail(controller, stack, service_id, containers):
    g = GossTool(controller, containers[0])
    g.command = 'not_existing'

    with pytest.raises(TestToolError, match='goss executable was not found'):
        g.run_goss()


def test__run__syntax_error__fail(controller, stack, service_id, containers):
    g = GossTool(controller, containers[0])
    g.command = '/goss/goss-linux-amd64 /data'

    with pytest.raises(TestToolError, match='Syntax error'):
        g.run_goss()


