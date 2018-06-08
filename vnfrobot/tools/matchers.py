import operator


def merge_two_dicts(x, y):
    """Given two dicts, merge them into a new dict as a shallow copy.

    source: https://stackoverflow.com/a/26853961/6112272
    """
    z = x.copy()
    z.update(y)
    return z


# For contains not, there is no direct operator available. We rely on the implicit knowledge that None means
# 'contains not'

equality_matchers = {
    'is': operator.eq,
    'is not': operator.ne,
}

existence_matchers = {
    'exists': operator.truth,
    'exists not': operator.not_,
}

number_matchers = dict(equality_matchers, **{
    'is greater': operator.gt,
    'is greater or equal': operator.ge,
    'is lesser': operator.lt,
    'is lesser or equal': operator.le
})

string_matchers_temp = dict(equality_matchers, **{
    'has': operator.eq,
    'has not': operator.ne,
    'contains': operator.contains,
    'contains not': 'contains_not',
    'is empty': 'is empty',
    'is not empty': 'is not empty',
})

string_matchers = merge_two_dicts(string_matchers_temp, existence_matchers)

all_matchers = dict(string_matchers, **number_matchers)

quoted_or_unquoted_string = """".+"|'.+'|\S+"""
