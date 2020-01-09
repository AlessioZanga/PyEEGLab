import logging
from abc import ABC, abstractmethod
from typing import List, Dict

from os import sched_getaffinity
from json import dumps
from hashlib import md5
from multiprocessing import Pool

from ..io import Raw


class Preprocessor(ABC):

    def __init__(self) -> None:
        logging.debug('Create new preprocessor')

    @abstractmethod
    def run(self, data: Raw, **kwargs):
        pass

    @abstractmethod
    def to_json(self) -> str:
        pass

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        value = md5(self.to_json()).hexdigest()
        value = int(value, 16)
        return value


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
        data.open().load_data()
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
        value = [p.to_json() for p in self.pipeline]
        value = dumps(value).encode()
        value = md5(value).hexdigest()
        value = int(value, 16)
        return value
