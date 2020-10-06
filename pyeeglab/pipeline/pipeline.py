import json
import hashlib
import logging

from multiprocessing import Pool, cpu_count

from typing import Dict, List

import numpy as np
import pandas as pd
import tqdm

from .preprocessor import Preprocessor


class Pipeline():

    environment: Dict = {}
    preprocessors: List[Preprocessor]

    def __init__(self, preprocessors: List[Preprocessor] = []) -> None:
        logging.info("Init preprocessing pipeline")
        self.preprocessors = preprocessors
        for p in preprocessors:
            logging.info("Init %s preprocessor", str(p))

    def _trigger_pipeline(self, annotation, **kwargs):
        data = None
        with annotation as reader:
            data = reader.load_data()
        try:
            for preprocessor in self.preprocessors:
                data = preprocessor(data, **kwargs)
        except ValueError as err:
            raise RuntimeError("{} with file id {}".format(err, annotation.file.uuid))
        return data

    def run(self, annotations: List) -> Dict:
        logging.debug("Environment variables: %s", str(self.environment))
        # Labels onehot encoding
        labels = [annotation.label for annotation in annotations]
        mapper = sorted(set(labels))
        labels = np.array([mapper.index(label) for label in labels])
        # Apply async pipeline to dataset
        pool = Pool(cpu_count())
        jobs = [
            pool.apply_async(
                func=self._trigger_pipeline,
                args=(annotation,),
                kwds=self.environment,
            )
            for annotation in annotations
        ]
        pool.close()
        # Iterate over async pool and report progress
        data = []
        for job in tqdm.tqdm(jobs):
            data.append(job.get())
        # Apply ToNumpy preprocessor to whole dataset
        if any([p.__class__.__name__ == "ToNumpy" for p in self.preprocessors]):
            data = np.array(data)
        return {"data": data, "labels": labels, "labels_encoder": mapper}

    def __hash__(self):
        key = [str(p) for p in self.preprocessors]
        key = json.dumps(key).encode()
        key = hashlib.md5(key).hexdigest()
        key = int(key, 16)
        return key
