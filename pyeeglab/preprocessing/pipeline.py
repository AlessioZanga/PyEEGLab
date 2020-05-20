import logging
from abc import ABC, abstractmethod
from typing import List, Dict

from os import sched_getaffinity
from json import loads, dumps
from numpy import array
from pandas import DataFrame
from hashlib import md5
from networkx import Graph
from multiprocessing import Pool

from ..io import Raw


class Preprocessor(ABC):

    def __init__(self) -> None:
        logging.debug('Create new preprocessor')

    @abstractmethod
    def run(self, data, **kwargs):
        pass

    def to_json(self) -> str:
        json = {self.__class__.__name__ : {}}
        json = dumps(json)
        return json

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        value = md5(self.to_json()).hexdigest()
        value = int(value, 16)
        return value


class JoinedPreprocessor(Preprocessor):

    def __init__(self, inputs: List, output: Preprocessor) -> None:
        super().__init__()
        logging.debug('Create new joinded preprocessor')
        self.inputs = inputs
        self.output = output

    def run(self, data, **kwargs):
        results = []
        for item in self.inputs:
            if isinstance(item, list):
                result = data
                for preprocessor in item:
                    result = preprocessor.run(result, **kwargs)
            if isinstance(item, Preprocessor):
                result = item.run(data, **kwargs)
            results.append(result)
        data = self.output.run(results, **kwargs)
        return data

    def to_json(self) -> str:
        inputs_json = []
        for i in self.inputs:
            if isinstance(i, list):
                j = [loads(p.to_json()) for p in i]
            if isinstance(i, Preprocessor):
                j = loads(i.to_json())
            inputs_json.append(j)
        output_json = loads(self.output.to_json())
        json = {
            self.__class__.__name__ : {
                'inputs': inputs_json,
                'output': output_json
            }
        }
        json = dumps(json)
        return json


class Pipeline():

    environment: Dict = {}
    pipeline: List[Preprocessor]

    def __init__(self, preprocessors: List[Preprocessor] = [], labels_mapping: Dict = None, to_numpy: bool = True) -> None:
        logging.debug('Create new preprocessing pipeline')
        self.pipeline = preprocessors
        self.labels_mapping = labels_mapping
        self.to_numpy = to_numpy

    def _trigger_pipeline(self, data: Raw, kwargs):
        data.open().load_data()
        for preprocessor in self.pipeline:
            data = preprocessor.run(data, **kwargs)
        return data

    def run(self, data: List[Raw]) -> Dict:
        labels = [raw.label for raw in data]
        data = [(d, self.environment) for d in data]
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.starmap(self._trigger_pipeline, data)
        pool.close()
        pool.join()
        if self.labels_mapping is not None:
            labels = [self.labels_mapping[label] for label in labels]
        onehot_encoder = sorted(set(labels))
        labels = array([onehot_encoder.index(label) for label in labels])
        if self.to_numpy:
            data = array(data)
        return {'data': data, 'labels': labels, 'labels_encoder': onehot_encoder}

    def to_json(self) -> str:
        json = [p.to_json() for p in self.pipeline]
        json = '[ ' + ', '.join(json) + ' ]'
        return json

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        value = [p.to_json() for p in self.pipeline]
        value = dumps(value).encode()
        value = md5(value).hexdigest()
        value = int(value, 16)
        return value


class VerticalPipeline(Pipeline):

    def _apply_args_and_kwargs(self, fn, data, kwargs):
        return fn(data, **kwargs)

    def _pre_trigger_pipeline(self, data: Raw) -> Raw:
        data.open().load_data()
        return data

    def _trigger_pipeline(self, preprocessor: Preprocessor, data: List[Raw]):
        data = [(preprocessor.run, d, self.environment) for d in data]
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.starmap(self._apply_args_and_kwargs, data)
        pool.close()
        pool.join()
        return data

    def run(self, data: List[Raw]) -> Dict:
        labels = [raw.label for raw in data]
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.map(self._pre_trigger_pipeline, data)
        pool.close()
        pool.join()
        if self.labels_mapping is not None:
            labels = [self.labels_mapping[label] for label in labels]
        for preprocessor in self.pipeline:
            data = self._trigger_pipeline(preprocessor, data)
        onehot_encoder = sorted(set(labels))
        labels = array([onehot_encoder.index(label) for label in labels])
        if not isinstance(data[0][0], Graph):
            data = array(data)
        return {'data': data, 'labels': labels, 'labels_encoder': onehot_encoder}
