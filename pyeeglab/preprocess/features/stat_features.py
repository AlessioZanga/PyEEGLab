from typing import List

import numpy as np
import pandas as pd
from scipy.integrate import simps

from ...pipeline import Preprocessor


class Mean(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.mean().to_frame(name='Mean') for d in data]


class Variance(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.var().to_frame(name='Variance') for d in data]


class Skewness(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.skew().to_frame(name='Skewness') for d in data]


class Kurtosis(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.kurt().to_frame(name='Kurtosis') for d in data]


class ZeroCrossing(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:

        def zero_crossing(array: np.ndarray) -> np.ndarray:
            return np.where(np.diff(np.sign(array)))[0].shape[0]

        return [
            d.apply(zero_crossing, raw=True).to_frame(name='Zero Crossing')
            for d in data
        ]


class AbsoluteArea(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:

        def absolute_area(array: np.ndarray) -> np.ndarray:
            return simps(np.abs(array), dx=1e-6)

        return [
            d.apply(absolute_area, raw=True).to_frame(name='Absolute Area')
            for d in data
        ]


class PeakToPeak(Preprocessor):
    def run(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:

        def pk2pk(array: np.ndarray) -> np.ndarray:
            return np.max(array) - np.min(array)

        return [
            d.apply(pk2pk, raw=True).to_frame(name='Peak To Peak')
            for d in data
        ]
