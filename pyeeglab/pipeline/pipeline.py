import logging
import json

import numpy as np
import pandas as pd

from hashlib import md5
from multiprocessing import Pool, cpu_count

from ..io import Raw
from .preprocessor import Preprocessor

from typing import Dict, List


class Pipeline():

    environment: Dict = {}
    pipeline: List[Preprocessor]

    def __init__(self, preprocessors: List[Preprocessor] = [], labels_mapping: Dict = None, to_numpy: bool = True, limit: float = 1) -> None:
        logging.debug('Create new preprocessing pipeline')
        self.pipeline = preprocessors
        self.labels_mapping = labels_mapping
        self.to_numpy = to_numpy
        self.limit = limit
    
    def _check_nans(self, data):
        nans = False
        if isinstance(data, np.ndarray):
            nans = np.any(np.isnan(data))
        if isinstance(data, pd.DataFrame):
            nans = data.isnull().values.any()
        return nans

    def _trigger_pipeline(self, data: Raw, kwargs):
        file_id = data.id
        data.open().load_data()
        for preprocessor in self.pipeline:
            data = preprocessor.run(data, **kwargs)
        
        nans = False
        if isinstance(data, list):
            nans = any([self._check_nans(d) for d in data])
        else:
            nans = self._check_nans(data)
        if nans:
            raise ValueError('Nans found in file with id {}'.format(file_id))

        return data

    def run(self, data: List[Raw]) -> Dict:
        logging.debug('Environment variables: {}'.format(
            str(self.environment)))
        limit = int(self.limit * len(data))
        labels = [raw.label for raw in data[:limit]]
        data = [(d, self.environment) for d in data[:limit]]
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
