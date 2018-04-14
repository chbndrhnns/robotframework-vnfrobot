import json

import pytest
from ruamel import yaml

from tools.goss.GossPort import GossPort

ports_test_data = [
    (
        {
            'data': {
                'ports': [
                    {
                        'port': 12345,
                        'protocol': 'udp',
                        'state': 'open',
                        'listening address': '127.0.0.1'
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'ports': [
                    {
                        'port': 12345,
                        'protocol': 'udp',
                        'listening': True,
                        'ip': ['127.0.0.1']
                    }
                ],
            },
        },
        {
            'expected_yaml': """port:

                  udp:12345:
                    listening: true
                    ip: 
                     - 127.0.0.1 
                """
        }
    ),
    ({
         'data': {
             'ports': [
                 {
                     'port': 8080,
                     'state': 'open',
                     'listening address': '127.0.0.1'
                 }
             ],
         },
     },
     {
         'with_mappings': {
             'ports': [
                 {
                     'port': 8080,
                     'protocol': 'tcp',
                     'listening': True,
                     'ip': ['127.0.0.1']
                 }
             ],
         },
     }, {
         'expected_yaml': u'port:\n\n  tcp:8080:\n    listening: True\n    ip: \n    - 127.0.0.1\n    \n'
     }),
    (
        {
            'data': {
                'ports': [
                    {
                        'port': 8081,
                        'state': 'closed',
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'ports': [
                    {
                        'port': 8081,
                        'protocol': 'tcp',
                        'listening': False
                    }
                ],
            },
        },
        {
            'expected_yaml': u'port:\n\n  tcp:8081:\n    listening: False\n'
        }
    )
]


@pytest.mark.parametrize('data, expected, yaml', ports_test_data)
def test__GossPort__apply_mappings__pass(data, expected, yaml):
    g = GossPort(data.get('data'))

    g.apply_mappings()

    expected = json.dumps(expected)
    actual = json.dumps(g.mapped)

    assert actual, expected


@pytest.mark.parametrize('data, mapped, out', ports_test_data)
def test__GossPort__transform__pass(data, mapped, out):
    g = GossPort(data.get('data'))

    g.transform()

    expected = yaml.safe_load(out.get('expected_yaml'))
    actual = g.out

    assert actual, expected
