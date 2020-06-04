import logging
import json

import numpy as np

from hashlib import md5
from multiprocessing import Pool, cpu_count

from ..io import Raw
from .preprocessor import Preprocessor

from typing import Dict, List


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
        logging.debug('Environment variables: {}'.format(
            str(self.environment)))
        labels = [raw.label for raw in data]
        data = [(d, self.environment) for d in data]
        pool = Pool(cpu_count())
        data = pool.starmap(self._trigger_pipeline, data)
        pool.close()
        pool.join()
        if self.labels_mapping is not None:
            labels = [self.labels_mapping[label] for label in labels]
        onehot_encoder = sorted(set(labels))
        labels = np.array([onehot_encoder.index(label) for label in labels])
        if self.to_numpy:
            data = np.array(data)
        return {'data': data, 'labels': labels, 'labels_encoder': onehot_encoder}

    def to_json(self) -> str:
        json = [p.to_json() for p in self.pipeline]
        json = '[ ' + ', '.join(json) + ' ]'
        return json

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        value = [p.to_json() for p in self.pipeline]
        value = json.dumps(value).encode()
        value = md5(value).hexdigest()
        value = int(value, 16)
        return value
