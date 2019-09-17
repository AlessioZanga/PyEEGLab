import logging
from abc import ABC, abstractmethod
from typing import List

from .raw import Raw
from ..database.index import Index


class DataLoader(ABC):
    _logger = logging.getLogger()

    def __init__(self) -> Index:
        self._logger.debug('Create data loader')
        self.index = None

    @abstractmethod
    def get_dataset(self) -> List[Raw]:
        pass

    @abstractmethod
    def get_channelset(self) -> List[str]:
        pass

    @abstractmethod
    def get_lowest_frequency(self) -> float:
        pass
