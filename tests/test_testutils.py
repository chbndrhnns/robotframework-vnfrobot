from testutils import get_truth
import operator


def test__get_truth__contains_string():
    inp = 'abcd efg'
    relate = operator.contains
    val = 'cd'

    res = get_truth(inp, relate, val)

    assert res == True


def test__get_truth__contains_list():
    inp = ['a', 'ab', 'abc']
    relate = operator.contains
    val = 'abc'

    res = get_truth(inp, relate, val)

    assert res == True

def test__get_truth__contains_not():
    inp = ['a', 'ab', 'abc']
    relate = 'contains_not'
    val = 'def'

    res = get_truth(inp, relate, val)

    assert res == True