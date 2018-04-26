ports_test_data = [
    (
        {
            'data': {
                'ports': [
                    {
                        'port': 80,
                        'protocol': 'tcp',
                        'state': 'open',
                        'listening address': []
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
                        'ip': [ ]
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