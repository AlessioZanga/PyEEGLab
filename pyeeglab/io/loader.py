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
    def getDataset(self):
        pass

    @abstractmethod
    def getDatasetText(self):
        pass

    @abstractmethod
    def getChannelSet(self):
        pass

    @abstractmethod
    def getLowestFrequency(self):
        pass
