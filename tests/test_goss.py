import json
import os
import tempfile
from time import sleep

import pytest
import yaml
from docker.models.containers import Container
from pytest import fixture

from exc import TestToolError, TransformationError
from tools.GossTool import GossTool
from tools.goss.GossPort import GossPort


def test__run__pass(controller, stack, service_id, gossfile, containers):
    stack_name = stack[0]

    controller.put_file(containers[0].id, gossfile)
    g = GossTool(controller, containers[0], gossfile=os.path.basename(gossfile))
    res = g.run()

    assert res['summary']['failed-count'] == 1


def test__run__gossfile_not_found__fail(controller, stack, service_id, containers):
    g = GossTool(controller, containers[0])
    g.gossfile = 'bla'

    with pytest.raises(TestToolError, match='Gossfile not found'):
        g.run()


def test__run__goss_not_found__fail(controller, stack, service_id, containers):
    g = GossTool(controller, containers[0])
    g.command = 'not_existing'

    with pytest.raises(TestToolError, match='goss executable was not found'):
        g.run()


def test__run__syntax_error__fail(controller, stack, service_id, containers):
    g = GossTool(controller, containers[0])
    g.command = '/goss/goss-linux-amd64 /data'

    with pytest.raises(TestToolError, match='Syntax error'):
        g.run()


def test__run__in_sidecar__pass(sidecar, gossfile_sidecar, network, volume_with_goss):
    controller = sidecar.get('controller')
    sidecar_name = sidecar.get('name')

    volumes = {
        volume_with_goss: {
            'bind': '/goss',
            'mode': 'ro'
        }
    }

    g = GossTool(controller, None, gossfile=os.path.basename(gossfile_sidecar))

    sidecar = controller.create_or_get_sidecar(
        image=sidecar.get('image'),
        command=g.command,
        network=network.name,
        volumes=volumes,
        name=sidecar_name
    )
    assert isinstance(sidecar, Container)
    controller.put_file(sidecar, gossfile_sidecar)
    res = controller.run_sidecar(sidecar=sidecar)
    j = json.loads(res.stdout)
    assert j['summary']['failed-count'] == 0


def test__run__in_sidecar_with_deployment__pass(sidecar, network, volume_with_goss, stack, service_id):
    controller = sidecar.get('controller')
    sidecar_name = sidecar.get('name')

    gossfile = \
        """addr:
            tcp://{}:80:
                reachable: true
        """.format(service_id)

    volumes = {
        volume_with_goss: {
            'bind': '/goss',
            'mode': 'ro'
        }
    }

    controller.connect_service_to_network(service_id, network.name)

    g = GossTool(controller, None)

    sidecar = controller.create_or_get_sidecar(
        image=sidecar.get('image'),
        command=g.command,
        network=network.name,
        volumes=volumes,
        name=sidecar_name
    )
    assert isinstance(sidecar, Container)

    with tempfile.NamedTemporaryFile() as f:
        f.write(gossfile)
        f.seek(0)
        controller.put_file(entity=sidecar, file_to_transfer=f.name,
                                                 filename='goss.yaml')
        sleep(10)
        res = controller.run_sidecar(sidecar=sidecar)

    assert len(res.stdout) > 0
    j = json.loads(res.stdout)
    assert j['summary']['failed-count'] == 0


# TODO: irgendwie muss auf ein ergebnis gewartet werden....