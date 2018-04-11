from string import Template

import yaml
import jinja2
from jinja2 import TemplateError

from exc import DataFormatError, ValidationError
from testutils import validate_context, validate_port, validate_property, validate_value, IpAddress
from tools.goss import GossTool


def generate_gossfile(context):
    try:
        g = \
            """
port:
  {{protocol }}:{{port}}:
    listening:{{state}}
    """
        rendered =  jinja2.Environment().from_string(g).render(context)

        # validate
        yaml.load(rendered)
    except (SyntaxError, TemplateError):
        raise DataFormatError('Error when generating the gossfile')

    return rendered


def validate(instance, raw_entity, raw_prop, matcher, raw_val):
    allowed_context = ['service', 'network']
    properties = {
        'state': ['open', 'closed'],
        'listening_address': IpAddress
    }

    expected_value = unicode(raw_val.strip('"\''))

    # Validations
    context = validate_context(allowed_context, instance.sut.target_type)
    port, protocol = validate_port(raw_entity)
    property = validate_property(properties, raw_prop)
    value = validate_value(properties, raw_prop, expected_value)

    condition = {'port': None}
    if 'state' in raw_prop:
        port_template = Template("$protocol:$port:")
        condition['port'] = {
            port_template.safe_substitute(protocol=protocol or 'tcp', port=port):
                {
                    'listening': value
                }
        }

    # Test
    # try:
    #     gossfile = generate_gossfile(condition)
    #     assert len(gossfile) > 0
    # except DataFormatError:
    #     raise

    # gossfile = yaml.dump(condition)
    gossfile = """port:
  tcp:12345:
    listening: false
    """

    containers = instance.docker_controller.get_containers_for_service(instance.sut.service_id)
    assert len(containers) > 0

    c = containers[0]

    instance.docker_controller.put_file(entity=c.id, file_to_transfer='goss.yaml', destination='/', content=gossfile)
    res = GossTool(controller=instance.docker_controller, target=c, gossfile='/goss.yaml').run_goss()

    assert isinstance(res['summary']['failed-count'], int)

    actual_value = res['results'][0]['found']
    if res['summary']['failed-count'] > 0:
        raise ValidationError('Port {}: {} {} {}, actual: {}'.format(raw_entity, raw_prop, matcher, expected_value, actual_value))

    assert True
