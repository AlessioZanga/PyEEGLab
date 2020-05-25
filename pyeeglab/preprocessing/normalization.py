import logging

import numpy as np
import pandas as pd

from json import dumps
from pandas import DataFrame
from typing import List

from .pipeline import Preprocessor


class MinMaxNormalization(Preprocessor):
    def run(self, data: pd.DataFrame, **kwargs) -> DataFrame:

        def min_max_norm(array: np.ndarray) -> np.ndarray:
            _max = np.max(array)
            _min = np.min(array)
            return (array - _min)/(_max - _min)

        return data.apply(min_max_norm, raw=True)


class MinMaxCentralizedNormalization(Preprocessor):
    def run(self, data: pd.DataFrame, **kwargs) -> DataFrame:

        def min_max_norm(array: np.ndarray) -> np.ndarray:
            _max = np.max(array)
            _min = np.min(array)
            return (array - ((_max + _min)/2))/((_max - _min)/2)

        return data.apply(min_max_norm, raw=True)
