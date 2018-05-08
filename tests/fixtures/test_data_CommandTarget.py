command_target_test_data_pass = [
    (['"sh --version"', 'stdout', 'contains', '"Free"']),
    (['"nginx -v"', 'return code', 'is', '0']),
    (['"sh --version"', 'stdout', 'contains not', '"Hello World"']),
    (['"sh --version"', 'stderr', 'contains', '" "']),
    (['sh --version', 'stdout', 'contains', '\'Free\''])
]

command_target_test_data_fail = [
    (['"sh --version"', 'stdout', 'contains', '']),
    (['"sh --version"', 'stdout', 'contains', '""']),
    (['"sh --version"', 'stout', 'contains not', '"Hello World"']),
    (['"sh --version"', 'stderr', 'is greater', '"a"']),
]

command_target_integration_test_data = [
    (
        {
            'test': [r"nginx -v", 'return code', 'is', '0'],
            'result': {
                'code': 0,
                'res': ''
            }
        }
    ),
    (
        {
            'test': [r"nginx -v", 'return code', 'is not', '1'],
            'result': {
                'code': 0,
                'res': ''
            }
        }
    ),
    (
        {
            'test': [r"echo bla", 'stdout', 'contains', '"bla"'],
            'result': {
                'code': 0,
                'res': 'bla'
            }
        }
    ),
    (
        {
            'test': [r"nginx -v", 'stdout', 'is', 'nginx version: nginx/1.13.12'],
            'result': {
                'code': 0,
                'res': 'nginx version: nginx/1.13.12'
            }
        }
    )

]