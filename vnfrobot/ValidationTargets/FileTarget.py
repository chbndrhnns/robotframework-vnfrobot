from ValidationTargets.ValidationTarget import ValidationTarget
from tools import validators, matchers
from tools.goss.GossFile import GossFile
from tools.testutils import validate_property, validate_value, validate_matcher, call_validator
from testtools.GossTool import GossTool


class File(ValidationTarget):
    allowed_contexts = ['service']
    properties = {
        'state': {
            'matchers': matchers.boolean_matchers,
            'values': ['existing']
        },
    }
    options = {
        'test_volume_required': True,
        'test_tool': GossTool,
        'transformation_handler': GossFile
    }

    def __init__(self, instance=None):
        super(File, self).__init__(instance)

    def validate(self):
        self._find_robot_instance()
        self._check_test_data()

        call_validator(self.instance.sut.target_type, validators.Service, File.allowed_contexts)
        self.property = validate_property(File.properties, self.property)
        validate_matcher([self.matcher], limit_to=File.properties.get('entity', {}).get('matchers', []))
        self.value = validate_value(File.properties, self.property, self.value)

    def _prepare_transform(self):
        # create exchange format
        self.data = {
            'files': [
                {
                    'file': self.entity
                }
            ]
        }
        f = self.data.get('files', [])[0]
        f.update({
            self.property: {
                'matcher': self.matcher,
                'value': self.value,
            }})

        # add properties that are implicitly necessary
        if 'state' not in self.property:
            f.update({
                'state': {
                    'matcher': 'is',
                    'value': 'existing',
                }})

    def _prepare_run(self, tool_instance):
        tool_instance.inject_gossfile(self)
