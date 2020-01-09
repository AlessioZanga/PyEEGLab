import logging
from abc import ABC, abstractmethod

from hashlib import md5

from ..io import DataLoader
from ..preprocessing import Pipeline

class Cache(ABC):

    def __init__(self) -> None:
        logging.debug('Create cache manager')

    def _get_cache_key(self, dataset: str, loader: DataLoader, pipeline: Pipeline) -> str:
        key = [loader, pipeline]
        key = [hash(k) for k in key]
        key = [str(k).encode() for k in key]
        key = [md5(k).hexdigest() for k in key]
        key = list(zip(['loader_', 'pipeline_'], key))
        key = [''.join(k) for k in key]
        key = dataset + '_' + ''.join(key)
        return key

    @abstractmethod
    def load(self, dataset: str, loader: DataLoader, pipeline: Pipeline):
        pass
