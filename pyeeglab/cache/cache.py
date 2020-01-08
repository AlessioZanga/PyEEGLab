import logging
from abc import ABC, abstractmethod

class Cache(ABC):

    def __init__(self) -> None:
        logging.debug('Create cache manager')

    @abstractmethod
    def load(self):
        pass
