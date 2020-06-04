import logging
import json

import numpy as np
import pandas as pd

from ...io import Raw
from ...pipeline import Preprocessor

from typing import List


class ToDataframe(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create DataFrame converter preprocessor')

    def run(self, data: Raw, **kwargs) -> pd.DataFrame:
        dataframe = data.open().to_data_frame()
        return dataframe


class ToNumpy(Preprocessor):

    def __init__(self, dtype: str = 'float32') -> None:
        super().__init__()
        logging.debug('Create Numpy (%s) converter preprocessor', dtype)
        self.dtype = dtype

    def to_json(self) -> str:
        out = {
            self.__class__.__name__: {
                'dtype': self.dtype
            }
        }
        out = json.dumps(out)
        return out

    def run(self, data: List[pd.DataFrame], **kwargs) -> List[np.ndarray]:
        data = [d.to_numpy(dtype=self.dtype) for d in data]
        return data


class ToNumpy1D(Preprocessor):

    def __init__(self, dtype: str = 'float32') -> None:
        super().__init__()
        logging.debug('Create Numpy 1D (%s) converter preprocessor', dtype)
        self.dtype = dtype

    def to_json(self) -> str:
        out = {
            self.__class__.__name__: {
                'dtype': self.dtype
            }
        }
        out = json.dumps(out)
        return out

    def run(self, data: List[pd.DataFrame], **kwargs) -> List[np.ndarray]:
        return [d.to_numpy(dtype=self.dtype).flatten() for d in data]


class ToMergedDataframes(Preprocessor):
    def run(self, data: List[List[pd.DataFrame]], **kwargs) -> List[pd.DataFrame]:
        return [pd.concat([d[i].T for d in data]).T for i, _ in enumerate(data[0])]


class CorrelationToAdjacency(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create adjacency converter preprocessor')

    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        mask = np.triu(np.ones(data[0].shape, dtype='bool'), k=1)
        data = [d.where(mask) for d in data]
        data = [d.stack().reset_index() for d in data]
        for d in data:
            d.columns = ['From', 'To', 'Weight']
        return data
