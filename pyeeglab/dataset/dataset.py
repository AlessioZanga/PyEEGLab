import logging
from abc import ABC, abstractmethod


class Dataset(ABC):
    _logger = logging.getLogger()

    @abstractmethod
    def load(self):
        pass
