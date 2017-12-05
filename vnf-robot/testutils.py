import inspect
import re


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


def run_keyword_tests(test_instance, tests=None, setup=None, expected_result=Result.PASS):
    caller_name = inspect.stack()[1][3]
    # TODO: verify that the expected method is called
    test_name = regex_method.findall(caller_name)[0]

    run_count = 0
    for t in tests:
        run_count += 1
        with test_instance.subTest(test=t):
            context = test_instance.suite.tests.create(u'Expect {}: {}'.format(Result.get(expected_result), t))
            context.keywords.create(t)
            result = test_instance.suite.run(options=test_instance.settings)

            if result.return_code > 1:
                test_instance.assertEqual(run_count, result.return_code, '\'{}\''.format(t))
            else:
                test_instance.assertEqual(expected_result, result.return_code, '\'{}\''.format(t))
