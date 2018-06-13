from abc import ABCMeta, abstractmethod

from DockerController import DockerController


class TestTool:
    """
    Base class for test tools

    """
    __metaclass__ = ABCMeta

    def __init__(self, controller, sut):
        """

        Args:
            controller: instance of InfrastructureController
            sut:  instance of SUT
        """
        self.controller = controller if isinstance(controller, DockerController) else None
        self.sut = sut
        self.target = None
        self._command = None
        self._test_results = None

    @abstractmethod
    def run(self, target):
        """
        Run the test tool

        Args:
            target: service or container

        Returns:
            None

        """
        raise NotImplementedError('must be implemented by the subclass')

    @abstractmethod
    def process_results(self, target):
        """
        Process results

        Args:
            target: service or container

        Returns:
            None

        """
        raise NotImplementedError('must be implemented by the subclass')

    @property
    def command(self):
        """
        Get the command the test tool runs

        Returns:
            str

        """
        return self._command

    @command.setter
    def command(self, value):
        """
        Set the command the test tool runs

        Args:
            value: str

        Returns:
            None

        """
        self._command = value

    @property
    def test_results(self):
        """
        Get test results

        Returns: str

        """
        return self._test_results

    @test_results.setter
    def test_results(self, value):
        """
        Set test results

        Args:
            value: str

        Returns:
            None

        """
        self._test_results = value

