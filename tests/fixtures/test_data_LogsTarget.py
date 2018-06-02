logs_target_test_data_pass = [
    (['', '', 'contains', 'Hello']),
]

logs_target_test_data_fail = [
    # (['', '', '', '']),
    (['', '', 'contains', '']),
]

logs_target_integration_test_data = [
    (
        {
            'test': ['', '', 'contains', 'GET / HTTP/1.1'],
            'result': {
                'code': 0,
                'res': '''10.255.0.2 - - [16/May/2018:07:51:49 +0000] "GET / HTTP/1.1" 200 612 "-" 
                "python-requests/2.18.4" "-" '''
            }
        }
    ),

]