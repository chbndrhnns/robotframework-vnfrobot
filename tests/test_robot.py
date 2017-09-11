import robot


def test_project_defines_author_and_version():
    assert hasattr(robot, '__author__')
    assert hasattr(robot, '__version__')
