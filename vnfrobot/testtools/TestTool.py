from abc import ABCMeta, abstractmethod

from DockerController import DockerController
from tools.testutils import timeit


class TestTool:
    __metaclass__ = ABCMeta

    def __init__(self, controller, sut):
        self.controller = controller if isinstance(controller, DockerController) else None
        self.sut = sut
        self._command = None
        self._test_results = None

    @abstractmethod
    def run(self):
        pass

    @property
    def command(self):
        return self._command

    @command.setter
    def command(self, value):
        self._command = value

    @property
    def test_results(self):
        return self._test_results

    @test_results.setter
    def test_results(self, value):
        self._test_results = value

    @abstractmethod
    def process_results(self, target):
        pass
