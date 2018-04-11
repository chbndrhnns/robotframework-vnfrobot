from exc import NotFoundError, ValidationError
from testutils import validate_context, validate_against_regex, get_truth, string_matchers


def validate(instance, raw_entity, matcher, raw_val):
    allowed_context = ['service']
    raw_entity_matcher = '[A-Z][A-Z0-9_]'
    raw_value_matcher = '[^\s]'

    expected_value = raw_val.strip('"\'')

    # Validations
    validate_context(allowed_context, instance.sut.target_type)
    validate_against_regex('variable', raw_entity, raw_entity_matcher)
    validate_against_regex('value', expected_value, raw_value_matcher)

    # Get data
    try:
        env = instance.docker_controller.get_env(instance.sut.service_id)
        actual_value = [e.split('=')[1] for e in env if raw_entity == e.split('=')[0]]
    except NotFoundError as exc:
        raise

    if not actual_value:
        raise ValidationError('No variable {} found.'.format(raw_entity))

    if not get_truth(actual_value[0], string_matchers[matcher], expected_value):
        raise ValidationError(
            'Variable {}: {} {}, actual: {}'.format(raw_entity, matcher, expected_value, actual_value[0]))
