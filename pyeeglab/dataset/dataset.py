import logging
from abc import ABC
from typing import Dict

from ..io import DataLoader
from ..cache import Cache, PickleCache
from ..pipeline import Pipeline

class Dataset(ABC):

    cache: Cache
    loader: DataLoader
    pipeline: Pipeline

    def __init__(self, loader: DataLoader) -> None:
        logging.debug('Create dataset')
        self.loader = loader
        self.set_cache_manager(PickleCache('export'))
        self.set_pipeline(Pipeline())

    def load(self) -> Dict:
        dataset = self.__class__.__name__.lower()
        return self.cache.load(dataset, self.loader, self.pipeline)

    def _get_dataset_env(self) -> Dict:
        return {
            'channels_set': self.loader.get_channels_set(),
            'lowest_frequency': self.loader.get_lowest_frequency(),
            'max_value': self.loader.get_max_value(),
            'min_value': self.loader.get_min_value(),
        }
    
    def set_minimum_event_duration(self, minimum_event_duration: float) -> 'Dataset':
        self.loader.set_minimum_event_duration(minimum_event_duration)
        return self

    def set_cache_manager(self, cache: Cache) -> 'Dataset':
        self.cache = cache
        return self

    def set_pipeline(self, pipeline: Pipeline) -> 'Dataset':
        self.pipeline = pipeline
        environment = self._get_dataset_env()
        self.pipeline.environment.update(environment)
        return self
