from testutils import validate_context, validate_port, validate_property, validate_value
import exc


def validate(instance, raw_entity, raw_prop, matcher, raw_val):
    allowed_context = ['service', 'network']
    properties = {
        'state': ['open', 'closed']
    }

    # Validations
    validate_context(allowed_context, instance.sut.target_type)
    validate_port(raw_entity)
    validate_property(properties, raw_prop)
    validate_value(properties, raw_prop, raw_val)

    # Test
