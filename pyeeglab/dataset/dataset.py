import logging
from abc import ABC

from ..io import DataLoader
from ..cache import Cache, SinglePickleCache
from ..preprocessing import Pipeline

class Dataset(ABC):

    cache: Cache
    loader: DataLoader
    pipeline: Pipeline

    def __init__(self) -> None:
        logging.debug('Create dataset')
        self.cache = SinglePickleCache('export')
        self.pipeline = Pipeline()

    def load(self):
        dataset = self.__class__.__name__.lower()
        return self.cache.load(dataset, self.loader, self.pipeline)

    def set_cache_manager(self, cache: Cache) -> 'Dataset':
        self.cache = cache
        return self

    def set_pipeline(self, pipeline: Pipeline) -> 'Dataset':
        self.pipeline = pipeline
        return self
