# -*- coding: utf-8 -*-
from abc import ABCMeta, abstractproperty, abstractmethod
from string import lower

from interfaces.ExternalTool import ExternalTool
from settings import Settings


class Goss(ExternalTool):
    def __init__(self, settings):
        super(Goss, self).__init__()

        self.settings = settings or Settings().tools['goss']
        ExternalTool.check_availability(self.settings['path'])

    def get_instance(self):
        pass

