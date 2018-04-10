class DataError(RuntimeError):
    # Could be False in case we do a dry run of the test cases before really running them
    ROBOT_EXIT_ON_FAILURE = False


class ParseError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = False


class AssertError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = False
    ROBOT_CONTINUE_ON_FAILURE = True


class DataFormatError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = False
    ROBOT_CONTINUE_ON_FAILURE = True


class SetupError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class ValidationError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = False


class TeardownError(RuntimeError):
    # ROBOT_EXIT_ON_FAILURE = True
    pass


class ConnectionError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = False
    ROBOT_CONTINUE_ON_FAILURE = True


class TimeoutError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = False
    ROBOT_CONTINUE_ON_FAILURE = True


class ArgumentMissingException(BaseException):
    pass


class InvalidPathException(BaseException):
    pass


class NotFoundError(RuntimeError):
    pass


class DeploymentError(RuntimeError):
    pass
