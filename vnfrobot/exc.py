class DataError(RuntimeError):
    # Could be False in case we do a dry run of the test cases before really running them
    ROBOT_EXIT_ON_FAILURE = False


class SetupError(RuntimeError):
    """
    Error that is thrown if the test setup fails.
    """
    ROBOT_EXIT_ON_FAILURE = True


class TestToolError(RuntimeError):
    """
    Error that is thrown if there is an error when running a test tool.
    """
    pass


class TransformationError(RuntimeError):
    """
    Error that is thrown if there is an error in the apply_mappings stage during value transformation.
    """
    pass


class ValidationError(RuntimeError):
    """
    Error that is thrown if a general validation error occurs. This can be either during the actual test or before a
    test when the keyword parameters are validated.
    """
    ROBOT_EXIT_ON_FAILURE = False
    ROBOT_CONTINUE_ON_FAILURE = False


class NotFoundError(RuntimeError):
    """
    Error that is thrown if an object is not found.
    """
    pass


class DeploymentError(RuntimeError):
    """
    Error that is thrown if there is a problem with a deployment.
    """
    pass
