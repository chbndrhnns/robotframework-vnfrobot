import collections
from collections import namedtuple

# data structures that are used in vnf-robot
SUT = collections.namedtuple('sut', 'target_type, target, service_id')
ProcessResult = namedtuple('ProcessResult', 'stdout stderr')
