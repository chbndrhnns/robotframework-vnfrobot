import collections
from collections import namedtuple

SUT = collections.namedtuple('sut', 'target_type, target, service_id')
ProcessResult = namedtuple('ProcessResult', 'stdout stderr')
