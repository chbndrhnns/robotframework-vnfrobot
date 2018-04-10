import inspect
import re

import operator
from string import lower

from pytest import fail
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

import exc

# For contains not, there is no direct operator available. We rely on the implicit knowledge that None means 'contains not'
string_matchers = {
    'is': operator.eq,
    'is not': operator.ne,
    'has': operator.eq,
    'has not': operator.ne,
    'exists': operator.truth,
    'exists not': operator.not_,
    'contains': operator.contains,
    'contains not': 'contains_not',
}

number_matchers = string_matchers.copy().update({
    'is greater': operator.gt,
    'is greater equal': operator.ge,
    'is lesser': operator.lt,
    'is lesser equal': operator.le
})


def get_truth(inp, relate, val):
    # special case: contains not is not covered by the operator module
    if relate == 'contains_not':
        return val not in inp
    # for operator.contains, the order of arguments is reversed
    if relate.__name__ == 'contains':
        return relate(inp, val)

    return relate(val, inp)


def validate_value(properties, raw_prop, raw_val):
    val = raw_val in properties[raw_prop]
    if not val:
        raise exc.ValidationError(
            'Value "{}" not allowed for {}. Must be any of {}'.format(raw_val, raw_prop, properties.keys()))


def validate_property(properties, raw_prop):
    # Check that the given property and its expected value are valid
    prop = raw_prop in properties
    if not prop:
        raise exc.ValidationError(
            'Property "{}" not allowed. Must be any of {}'.format(raw_prop, properties.keys()))


def validate_against_regex(context, raw_value, regex):
    found = re.search(regex, raw_value)
    if not found:
        raise exc.ValidationError('Value "{}" not valid for {}'.format(raw_value, context))


def validate_port(raw_entity):
    # Check that raw_entity is valid
    # 0 < port <= 65535
    # \d+
    entity = re.search('(\d+)[/]?(tcp|udp)?', raw_entity, re.IGNORECASE)
    if not entity:
        raise exc.ValidationError(
            'Port "{}" not valid.'.format(raw_entity))
    port = int(entity.group(1)) if entity else None
    protocol = lower(entity.group(2)) if entity.group(2) else None
    if not (0 < port <= 65535):
        raise exc.ValidationError(
            'Port "{}" not valid. Must be between 1 and 65535'.format(port))
    elif protocol:
        if protocol not in ['tcp', 'udp']:
            raise exc.ValidationError(
                'Protocol "{}" not valid. Only udp and tcp are supported'.format(protocol))


def validate_context(allowed_context, target_type):
    # Check that a context is given for the test
    if target_type not in allowed_context:
        raise exc.SetupError(
            'Context type "{}" not allowed. Must be any of {}'.format(target_type, allowed_context))


class Result:
    def __init__(self):
        pass

    PASS = 0
    FAIL = 1

    map = {'PASS': 0, '0': 'PASS', '1': 'FAIL', 'FAIL': 1}

    @classmethod
    def get(cls, key):
        return cls.map.get(str(key))


regex_method = re.compile('test__(\w+)__\w+')


def _add_host_context(self, suite=None, host=None):
    if suite is None:
        return None
    if host is None:
        return None

    context = 'Set context to {}'.format(host)
    return suite.keywords.create(context, type='setup')


def run_keyword_tests(test_instance, tests=None, setup=None, expected_result=Result.PASS, expected_message=None):
    caller_name = inspect.stack()[1][3]
    # TODO: verify that the expected method is called
    test_name = regex_method.findall(caller_name)[0]

    run_count = 0
    context = test_instance.suite.tests
    for t in tests:
        run_count += 1
        with test_instance.subTest(test=t):
            test = context.create(u'Expect {}: {}'.format(Result.get(expected_result), t))
            test.keywords.append(t)

    result = test_instance.suite.run(output=None)

    if expected_result is Result.FAIL:
        test_instance.assertEqual(run_count, result.statistics.total.all.failed,
                                  'Expected failure count does not match actual failure count.')
    if expected_result is Result.PASS:
        test_instance.assertEqual(run_count, result.statistics.total.all.passed,
                                  'Expected pass count does not match actual pass count.')

    if expected_message:
        for result in result.suite.tests:
            test_instance.assertIn(expected_message, result.message)
