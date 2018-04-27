###
# Structure
# (
# {<data that comes from the robot test file>},
# {<data that can be given to the GossEntity>},
# {<data that comes back from the GossEntity>},
# {<gossfile that is used to validate>}
# )
###

port_target_test_data_pass = [
    (['6379/TCP', 'state', 'is', 'open']),
    (['6379/udp', 'state', 'is', 'open']),
    (['8080', 'state', 'is', 'open']),
    (['8080', 'listening address', 'is', '::']),
    (['8080', 'listening address', 'is', '127.0.0.1']),
]

port_target_test_data_fail = [

    (['66000', 'state', 'is', 'open']),
    (['6379/ABC', 'state', 'is', 'open']),
    (['6379', 'listeningaddress', 'is', '127.0.0.1']),
    (['6379', 'listening_address', 'is', 'open']),

]

ports_test_data = [
    (
        {
            'test': ['80', 'state', 'is', 'open']
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
            'test': ['12345/udp', 'listening address', 'is', '127.0.0.1']
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
    (
        {
            'test': ['8080/tcp', 'listening address', 'contains', '127.0.0.1']
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
            'test': ['8081', 'state', 'is', 'closed']
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
