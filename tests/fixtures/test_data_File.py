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
]

file_target_test_data_fail = [
    (['/bin/sh', 'blaa', 'is', 'existing']),
    (['/bin/sh', 'blaa', 'has', 'existing']),
    (['/bin/sh', 'state', 'is', 'there']),
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
]
