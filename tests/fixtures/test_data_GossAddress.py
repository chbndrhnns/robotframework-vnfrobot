
###
# Structure
# (
# {<data that can be given to the GossEntity>},
# {<data that comes back from the GossEntity>},
# {<gossfile that is used to validate>}
# )
###
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

###
# Structure
# (
# {<data that can be given to the GossEntity>},
# {<return value from goss>}
# )
###
goss_results = [
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
        r"""{
            "results": [
                {
                    "duration": 26609600,
                    "err": null,
                    "expected": [
                        "true"
                    ],
                    "found": [
                        "true"
                    ],
                    
                    "meta": null,
                    "property": "reachable",
                    "resource-id": "tcp://www.google.com:80",
                    "resource-type": "Addr",
                    "result": 0,
                    "successful": true,
                    "summary-line": "Addr: tcp://www.google.cdom:80: reachable:\nExpected\n    <bool>: true\nto equal\n    <bool>: true",
                    "test-type": 0,
                    "title": ""
                }
            ],
            "summary": {
                "failed-count": 0,
                "summary-line": "Count: 1, Failed: 0, Duration: 0.027s",
                "test-count": 1,
                "total-duration": 27076200
            }
        }"""
    ),
]
