import logging
from abc import ABC

from ..io import DataLoader
from ..cache import Cache
from ..preprocessing import Pipeline

class Dataset(ABC):

    cache: Cache
    loader: DataLoader
    pipeline: Pipeline

    def __init__(self) -> None:
        logging.debug('Create dataset')

    def load(self):
        return self.cache.load()

    def set_cache_manager(self, cache: Cache) -> 'Dataset':
        self.cache = cache
        return self

    def set_pipeline(self, pipeline: Pipeline) -> 'Dataset':
        self.pipeline = pipeline
        return self
