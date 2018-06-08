from ValidationTargets.ValidationTarget import ValidationTarget
from testtools.DockerTool import DockerTool
from tools import validators


class SkeletonTarget(ValidationTarget):
    allowed_contexts = []
    properties = {
        'a_property': {
            'matchers': ['is'],
            'values': ['val_a', 'val_b']
        },
        'b_property': {
            'matchers': ['is'],
            'values': validators.IpAddress
        }
    }
    options = {
        'test_volume_required': False,
        'test_tool': DockerTool,
    }

    def __init__(self, instance=None):
        super(SkeletonTarget, self).__init__(instance)
        self.data = None

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()

        # call validators for every parameter that is provided to the class

    def _prepare_transform(self):
        # If a transformation of the input data is required, call the procedures here
        pass

    def _prepare_run(self, tool_instance):
        # If actions are required prior to the test run, add them here.
        pass
