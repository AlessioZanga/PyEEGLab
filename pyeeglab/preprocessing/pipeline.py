import logging
from abc import ABC, abstractmethod
from typing import List

from os import sched_getaffinity
from multiprocessing import Pool

from ..io import Raw


class Preprocessor(ABC):

    def __init__(self) -> None:
        logging.debug('Create new preprocessor')

    @abstractmethod
    def run(self, data: Raw):
        pass


class Pipeline():

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

    def _trigger_pipeline(self, data: Raw):
        for preprocessor in self.pipeline:
            data = preprocessor.run(data)
        return data

    def run(self, data: List[Raw]) -> List:
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.map(self._trigger_pipeline, data)
        pool.close()
        pool.join()
        return data
