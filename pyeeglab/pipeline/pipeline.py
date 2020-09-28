import json
import logging

from hashlib import md5
from os.path import join
from multiprocessing import Pool, cpu_count

from typing import Dict, List

import numpy as np
import pandas as pd

from .preprocessor import Preprocessor


class Pipeline():

    environment: Dict = {}
    pipeline: List[Preprocessor]

    def __init__(self, preprocessors: List[Preprocessor] = [], labels_mapping: Dict = None) -> None:
        logging.debug('Create new preprocessing pipeline')
        self.pipeline = preprocessors
        self.labels_mapping = labels_mapping
    
    def _check_nans(self, data):
        nans = False
        if isinstance(data, np.ndarray):
            nans = np.any(np.isnan(data))
        if isinstance(data, pd.DataFrame):
            nans = data.isnull().values.any()
        return nans

    def _trigger_pipeline(self, annotation, kwargs):
        data = None

        with annotation as reader:
            data = reader.load_data()
            for preprocessor in self.pipeline:
                data = preprocessor.run(data, **kwargs)
        
        nans = False
        if isinstance(data, list):
            nans = any([self._check_nans(d) for d in data])
        else:
            nans = self._check_nans(data)
        if nans:
            raise ValueError('Nans found in file with id {}'.format(annotation.file_uuid))

        return data

    def run(self, data) -> Dict:
        logging.debug('Environment variables: {}'.format(
            str(self.environment)
        ))
        labels = [raw.label for raw in data]
        data = [(d, self.environment) for d in data]
        pool = Pool(cpu_count())
        data = pool.starmap(self._trigger_pipeline, data)
        pool.close()
        pool.join()
        if self.labels_mapping is not None:
            labels = [self.labels_mapping[label] for label in labels]
        onehot_encoder = sorted(set(labels))
        class_id = self.environment.get('class_id', None)
        if class_id in onehot_encoder:
            onehot_encoder.remove(class_id)
            onehot_encoder = [class_id] + onehot_encoder
        labels = np.array([onehot_encoder.index(label) for label in labels])
        if any([p.__class__.__name__ == 'ToNumpy' for p in self.pipeline]):
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
