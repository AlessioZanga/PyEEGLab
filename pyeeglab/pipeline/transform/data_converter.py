from dataclasses import dataclass

from typing import List

import numpy as np
import pandas as pd

from mne.io import Raw

from ..preprocessor import Preprocessor


@dataclass
class ToDataframe(Preprocessor):

    def __call__(self, data: Raw, **kwargs) -> pd.DataFrame:
        data = data.to_data_frame().drop("time", axis=1)
        if data.isnull().values.any():
            raise ValueError("Nan found during preprocessing")
        return data


@dataclass
class ToNumpy(Preprocessor):

    dtype: str = "float32"

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[np.ndarray]:
        data = np.array([d.to_numpy(dtype=self.dtype) for d in data])
        if np.any(np.isnan(data)):
            raise ValueError("Nan found during preprocessing")
        return data


@dataclass
class ToMergedDataframes(Preprocessor):

    def __call__(self, data: List[List[pd.DataFrame]], **kwargs) -> List[pd.DataFrame]:
        return [pd.concat([d[i].T for d in data]).T for i, _ in enumerate(data[0])]


@dataclass
class CorrelationToAdjacency(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        mask = np.triu(np.ones(data[0].shape, dtype="bool"), k=1)
        data = [d.where(mask) for d in data]
        data = [d.stack().reset_index() for d in data]
        for d in data:
            d.columns = ["From", "To", "Weight"]
        return data
