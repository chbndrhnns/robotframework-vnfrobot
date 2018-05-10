import operator

# For contains not, there is no direct operator available. We rely on the implicit knowledge that None means
# 'contains not'

boolean_matchers = {
    'is': operator.eq,
    'is not': operator.ne,
}
number_matchers = dict(boolean_matchers, **{
    'is greater': operator.gt,
    'is greater equal': operator.ge,
    'is lesser': operator.lt,
    'is lesser equal': operator.le
})

string_matchers = dict(boolean_matchers, **{
    'has': operator.eq,
    'has not': operator.ne,
    'exists': operator.truth,
    'exists not': operator.not_,
    'contains': operator.contains,
    'contains not': 'contains_not',
})

all_matchers = dict(string_matchers, **number_matchers)

quoted_or_unquoted_string = """".+"|'.+'|\S+"""
