placement_target_test_data = [
    (
        {
            'test': ['', 'node.role', 'contains', 'manager']
        }
    ),
    (
        {
            'test': ['', 'node.role', 'is', 'manager']
        }
    )

]

placement_target_test_data_fail = [
    (
        {
            'test': ['', 'node.role', 'contains bla', 'manager']
        }
    ),
    (
        {
            'test': ['', 'hostingrolebla', 'contains', 'manager']
        }
    ),
    (
        {
            'test': ['', 'node.role', 'is greater', 'manager']
        }
    ),
    (
        {
            'test': ['', 'node.role', 'is', '  ']
        }
    ),
]