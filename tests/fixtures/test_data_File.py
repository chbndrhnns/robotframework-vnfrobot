###
# Structure
# (
# {<data that comes from the robot test file>},
# {<data that can be given to the GossEntity>},
# {<data that comes back from the GossEntity>},
# {<gossfile that is used to validate>}
# )
###

file_target_test_data_pass = [
    (['/bin/sh', 'state', 'is', 'existing']),
    (['/bin/sh', 'state', 'is not', 'existing']),
    (['/bin/sh', 'mode', 'is', 'executable']),
    (['/bin/sh', 'mode', 'is', '0777']),
]

file_target_test_data_fail = [
    (['/bin/sh', 'blaa', 'is', 'existing']),
    (['/bin/sh', 'blaa', 'has', 'existing']),
    (['/bin/sh', 'state', 'is', 'there']),
    (['/bin/sh', 'mode', 'is', 'blu']),
    (['/bin/sh', 'mode', 'is', '18f200']),
]

file_test_data = [
    (
        {
            'test': ['/bin/sh', 'state', 'is', 'existing']
        },
        {
            'data': {
                'files': [
                    {
                        'file': '/bin/sh',
                        'state': {
                            'matcher': 'is',
                            'value': 'existing',
                        }
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'files': [
                    {
                        'file': '/bin/sh',
                        'exists': True,
                    }
                ],
            },
        },
        {
            'expected_yaml': """file:
                  /bin/sh:
                    exists: true
                """
        }
    ),
    (
        {
            'test': ['/bin/sh', 'mode', 'is', 'executable']
        },
        {
            'data': {
                'files': [
                    {
                        'file': '/bin/sh',
                        'state': {
                            'matcher': 'is',
                            'value': 'existing',
                        },
                        'mode': {
                            'matcher': 'is',
                            'value': 'executable'
                        }
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'files': [
                    {
                        'file': '/bin/sh',
                        'exists': True,
                        'mode': '0777'
                    }
                ],
            },
        },
        {
            'expected_yaml': """file:
                  /bin/sh:
                    exists: true
                    mode: "0777"
                """
        }
    ),
    (
        {
            'test': ['/etc/hosts', 'content', 'contains', 'localhost']
        },
        {
            'data': {
                'files': [
                    {
                        'file': '/etc/hosts',
                        'state': {
                            'matcher': 'is',
                            'value': 'existing',
                        },
                        'content': {
                            'matcher': 'contains',
                            'value': 'localhost'
                        }
                    }
                ],
            },
        },
        {
            'with_mappings': {
                'files': [
                    {
                        'file': '/etc/hosts',
                        'exists': True,
                        'contains': 'localhost'
                    }
                ],
            },
        },
        {
            'expected_yaml': """file:
              /etc/hosts:
                exists: true
                contains: 
                - 'localhost'
            """
        }
    ),
]
