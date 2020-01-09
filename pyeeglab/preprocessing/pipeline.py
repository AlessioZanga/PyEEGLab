import logging
from abc import ABC, abstractmethod
from typing import List, Dict

from os import sched_getaffinity
from multiprocessing import Pool

from ..io import Raw


class Preprocessor(ABC):

    def __init__(self) -> None:
        logging.debug('Create new preprocessor')

    @abstractmethod
    def run(self, data: Raw, **kwargs):
        pass

    @abstractmethod
    def __eq__(self, other):
        pass

    @abstractmethod
    def __hash__(self):
        pass


class Pipeline():

    options: Dict = {}
    pipeline: List[Preprocessor] = []

    def __init__(self, preprocessors: List[Preprocessor] = []) -> None:
        logging.debug('Create new preprocessing pipeline')
        self.add_all(preprocessors)

    def add(self, preprocessor: Preprocessor) -> 'Pipeline':
        self.pipeline.append(preprocessor)
        return self

    def add_all(self, preprocessors: List[Preprocessor]) -> 'Pipeline':
        self.pipeline += preprocessors
        return self

    def _trigger_pipeline(self, data: Raw, kwargs):
        for preprocessor in self.pipeline:
            data = preprocessor.run(data, **kwargs)
        return data

    def run(self, data: List[Raw]) -> List:
        labels = [raw.label for raw in data]
        data = [(d, self.options) for d in data]
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.starmap(self._trigger_pipeline, data)
        pool.close()
        pool.join()
        return {'data': data, 'labels': labels}

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        value = [hash(p) for p in self.pipeline]
        value = tuple(value)
        return hash(value)
