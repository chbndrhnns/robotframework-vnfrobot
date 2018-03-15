import inspect
import re

from pytest import fail
from robot.api import logger


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

    result = test_instance.suite.run(options=test_instance.settings)

    if expected_result is Result.FAIL:
        test_instance.assertEqual(run_count, result.statistics.total.all.failed,
                                  'Expected failure count does not match actual failure count.')
    if expected_result is Result.PASS:
        test_instance.assertEqual(run_count, result.statistics.total.all.passed,
                                  'Expected pass count does not match actual pass count.')

    if expected_message:
        for result in result.suite.tests:
            test_instance.assertIn(expected_message, result.message)

