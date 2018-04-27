
###
# Structure
# (
# {<data that comes from the robot test file>},
# {<data that can be given to the GossEntity>},
# {<data that comes back from the GossEntity>},
# {<gossfile that is used to validate>}
# )
###
ports_test_data = [
    (
        {
            'input': ['80', 'state', 'is', 'open']
        },
        {
            'data': {
                'ports': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'state': {
                            'matcher': 'is',
                            'value': 'open',
                        }
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'ports': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'listening': True,
                    }
                ],
            },
        },
        {
            'expected_yaml': """port:
                  tcp:80:
                    listening: true
                """
        }
    ),
    (
        {
            'input': ['1234/udp', 'listening address', 'is', '127.0.0.1']
        },
        {
            'data': {
                'ports': [
                    {
                        'port': 12345,
                        'protocol': 'udp',
                        'state': {
                            'matcher': 'is',
                            'value': 'open',
                        },
                        'listening address': {
                            'matcher': 'is',
                            'value': '127.0.0.1',
                        }
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
                        'ip': [ '127.0.0.1']
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
    (
        {
            'input': ['8080/tcp', 'listening address', 'contains', '127.0.0.1']
        },
        {
            'data': {
                'ports': [
                    {
                        'port': 8080,
                        'state': {
                            'matcher': 'is',
                            'value': 'open'
                        },
                        'listening address': {
                            'matcher': 'is',
                            'value': '127.0.0.1'
                        }
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
            'input': ['8081', 'state', 'is', 'closed']
        },
        {
            'data': {
                'ports': [
                    {
                        'port': 8081,
                        'state': {
                            'matcher': 'is',
                            'value': 'closed'
                        },
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
