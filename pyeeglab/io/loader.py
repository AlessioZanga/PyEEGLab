import logging
from abc import ABC, abstractmethod
from typing import List

from .raw import Raw


class DataLoader(ABC):

    def __init__(self) -> None:
        logging.debug('Create data loader')
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
