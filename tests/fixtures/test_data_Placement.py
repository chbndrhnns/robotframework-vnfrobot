placement_target_test_data = [
    (
        {
            'test': ['placement', 'node.role', 'is', 'manager'],
            'result': {u'Spec': {u'Labels': {}, u'Role': u'manager', u'Availability': u'active'},}
        }
    ),
    (
        {
            'test': ['placement', 'node.role', 'is not', 'abc'],
            'result': {u'Spec': {u'Labels': {}, u'Role': u'client', u'Availability': u'active'},}
        }
    ),

]

placement_target_test_data_fail = [
    (
        {
            'test': ['placement', 'node.role', 'contains bla', 'manager'],
            'result': {}
        }
    ),
    (
        {
            'test': ['placement', 'hostingrolebla', 'contains', 'manager'],
            'result': {}
        }
    ),
    (
        {
            'test': ['placement', 'node.role', 'is greater', 'manager'],
            'result': {}
        }
    ),
    (
        {
            'test': ['placement', 'node.role', 'is', '  '],
            'result': {}
        }
    ),
]
