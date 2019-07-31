import logging
from abc import ABC, abstractmethod


class DataLoader(ABC):
    _index = None
    _logger = logging.getLogger()

    def __init__(self):
        self._logger.debug('Create data loader')

    def index(self):
        return self._index

    @abstractmethod
    def get_dataset(self):
        pass

    @abstractmethod
    def get_dataset_text(self):
        pass

    @abstractmethod
    def get_channelset(self):
        pass

    @abstractmethod
    def get_lowest_frequency(self):
        pass
