class DataError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class SetupError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True


class TeardownError(RuntimeError):
    # ROBOT_EXIT_ON_FAILURE = True
    pass


class ConnectionError(RuntimeError):
    ROBOT_EXIT_ON_FAILURE = True
