import pytest
from ruamel import yaml

from tools.goss.GossAddr import GossAddr
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
                     'listening': True,
                     'ip': ['127.0.0.1']
                 }
             ],
         },
     }, {
         'expected_yaml': u'port:\n\n  tcp:8080:\n    listening: True\n    ip: \n    - 127.0.0.1\n    \n'
     }
    ),
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

addresses_test_data = [
    (
        {
            'data': {
                'addresses': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'address': 'www.google.com',
                        'state': 'is reachable'
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'addresses': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'address': 'www.google.com',
                        'reachable': True
                    }
                ],
            },
        },
        {
            'expected_yaml': """addr:
                  tcp://www.google.com:80:
                    reachable: true
                    timeout: 1000 
                """
        }
    ),
    (
        {
            'data': {
                'addresses': [
                    {
                        'port': 8081,
                        'protocol': 'udp',
                        'address': 'www.google.co.uk',
                        'state': 'is not reachable'
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'addresses': [
                    {
                        'port': 8081,
                        'protocol': 'udp',
                        'address': 'www.google.co.uk',
                        'reachable': False
                    }
                ],
            },
        },
        {
            'expected_yaml': """addr:
                  udp://www.google.co.uk:8081:
                    reachable: false
                    timeout: 1000 
                """
        }
    ),
]


@pytest.mark.parametrize('data, expected, yaml', ports_test_data)
def test__GossPort__apply_mappings__pass(data, expected, yaml):
    g = GossPort(data.get('data'))

    g.apply_mappings()

    expected = expected.get('with_mappings')
    actual = g.mapped

    assert actual == expected


@pytest.mark.parametrize('data, mapped, out', ports_test_data)
def test__GossPort__transform__pass(data, mapped, out):
    g = GossPort(data.get('data'))

    g.transform()

    expected = yaml.safe_load(out.get('expected_yaml'))
    actual = yaml.safe_load(g.out)

    assert actual == expected


@pytest.mark.parametrize('data, expected, yaml', addresses_test_data)
def test__GossAddr__apply_mappings__pass(data, expected, yaml):
    g = GossAddr(data.get('data'))

    g.apply_mappings()

    expected = expected.get('with_mappings')
    actual = g.mapped

    assert actual == expected


@pytest.mark.parametrize('data, mapped, out', addresses_test_data)
def test__GossAddr__transform__pass(data, mapped, out):
    g = GossAddr(data.get('data'))

    g.transform()

    expected = yaml.safe_load(out.get('expected_yaml'))
    actual = yaml.safe_load(g.out)

    assert actual == expected
