import logging
from abc import ABC
from typing import Dict

from ..io import DataLoader
from ..cache import Cache, SinglePickleCache
from ..preprocessing import Pipeline

class Dataset(ABC):

    cache: Cache
    loader: DataLoader
    pipeline: Pipeline

    def __init__(self, loader: DataLoader) -> None:
        logging.debug('Create dataset')
        self.loader = loader
        self.set_cache_manager(SinglePickleCache('export'))
        self.set_pipeline(Pipeline())

    def load(self) -> Dict:
        dataset = self.__class__.__name__.lower()
        return self.cache.load(dataset, self.loader, self.pipeline)

    def _get_dataset_options(self) -> Dict:
        return {
            'channel_set': self.loader.get_channelset(),
            'lowest_frequency': self.loader.get_lowest_frequency()
        }

    def set_cache_manager(self, cache: Cache) -> 'Dataset':
        self.cache = cache
        return self

    def set_pipeline(self, pipeline: Pipeline) -> 'Dataset':
        self.pipeline = pipeline
        options = self._get_dataset_options()
        self.pipeline.options.update(options)
        return self
