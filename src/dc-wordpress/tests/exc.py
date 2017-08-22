class DataError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class SetupError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class ConnectionError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True
