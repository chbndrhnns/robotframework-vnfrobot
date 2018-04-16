import inspect
import re

import operator
from abc import abstractmethod, ABCMeta
from string import lower

import ipaddress
import validators
from pytest import fail
from robot.api import logger
from robot.libraries.BuiltIn import BuiltIn

import exc

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


def get_truth(inp, relate, val):
    # special case: contains not is not covered by the operator module
    if relate == 'contains_not':
        return val not in inp
    # for operator.contains, the order of arguments is reversed
    if relate.__name__ == 'contains':
        return relate(inp, val)

    return relate(val, inp)


def validate_matcher(matchers, limit_to=None):
    if limit_to is None:
        limit_to = []

    invalid = [m for m in matchers if m not in string_matchers.keys()]
    if invalid:
        raise exc.ValidationError('Matchers {} not allowed here.'.format(invalid))

    if limit_to:
        invalid = [m for m in matchers if m not in limit_to]
        if invalid:
            raise exc.ValidationError('Matchers {} not allowed here.'.format(invalid))


def validate_entity(entity, validator):
    try:
        v = validator()
        if isinstance(v, Validator):
            return v.validate(entity)
        else:
            raise exc.ValidationError('Value {} not allowed here. Expected: {}'.format(entity, v.name))
    except Exception:
        raise


def validate_value(properties, property, value):
    validator = properties[property]

    if isinstance(validator.get('values'), list):
        valid = value in properties.get(property, {}).get('values', {})
        if not valid:
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(value, property, properties[property]))
    elif isinstance(validator.get('value')(), Validator):
        v = validator.get('value')()
        if not v.validate(value):
            raise exc.ValidationError(
                'Value "{}" not allowed for {}. Must be any of {}'.format(value, property, v.name))

    return value


def validate_property(properties, raw_prop):
    # Check that the given property is valid
    if not properties.get(raw_prop, None):
        raise exc.ValidationError(
            'Property "{}" not allowed. Must be any of {}'.format(raw_prop, properties.keys()))

    return raw_prop


def validate_against_regex(context, raw_value, regex):
    found = re.search(regex, raw_value)
    if not found:
        raise exc.ValidationError('Value "{}" not valid for {}'.format(raw_value, context))


def validate_port(raw_entity):
    # Check that raw_entity is valid
    # 0 < port <= 65535
    # \d+
    entity = re.search('(\d+)[/]?(\w{,3})?', raw_entity, re.IGNORECASE)
    if not entity:
        raise exc.ValidationError(
            'Port "{}" not valid.'.format(raw_entity))
    port = int(entity.group(1)) if entity else None
    protocol = entity.group(2) if entity.groups is not None else None
    if not (0 < port <= 65535):
        raise exc.ValidationError(
            'Port "{}" not valid. Must be between 1 and 65535'.format(port))
    if len(protocol) > 0 and lower(protocol) not in ['tcp', 'udp']:
        raise exc.ValidationError(
            'Protocol "{}" not valid. Only udp and tcp are supported'.format(protocol))

    return port, protocol


def validate_context(allowed_context, given_context):
    # Check that a context is given for the test
    if given_context not in allowed_context:
        raise exc.SetupError(
            'Context type "{}" not allowed. Must be any of {}'.format(given_context, allowed_context))

    return given_context


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


class Validator:
    __metaclass__ = ABCMeta

    def __init__(self):
        pass

    @staticmethod
    @abstractmethod
    def validate(entity):
        pass


class Url(Validator):
    def __init__(self):
        Validator.__init__(self)
        self.name = 'URL'

    @staticmethod
    def validate(val):
        return validators.url(val)


class Domain(Validator):
    def __init__(self):
        Validator.__init__(self)
        self.name = 'Domain'

    @staticmethod
    def validate(val):
        try:
            return validators.domain(val)
        except Exception:
            pass


class IpAddress(Validator):
    def __init__(self):
        Validator.__init__(self)
        self.name = 'IP address'

    @staticmethod
    def validate(val):
        try:
            return validators.ipv4(val) or (validators.ipv6(val))
        except Exception:
            pass

def str2bool(val):
    return val.lower() in ("yes", "true", "t", "1")
