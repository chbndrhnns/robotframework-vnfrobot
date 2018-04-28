def set_test_data(e, test):
    if len(test) == 4:
        e.set('entity', test[0])
        e.set('property', test[1])
        e.set('matcher', test[2])
        e.set('value', test[3])
    elif len(test) == 3:
        e.set('entity', test[0])
        e.set('property', test[0])
        e.set('matcher', test[1])
        e.set('value', test[2])