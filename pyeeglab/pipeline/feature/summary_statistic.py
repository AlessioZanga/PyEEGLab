from typing import List

from dataclasses import dataclass

import numpy as np
import pandas as pd
import scipy

from ..preprocessor import Preprocessor


@dataclass
class Mean(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.mean().to_frame(name="Mean") for d in data]


@dataclass
class Variance(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.var().to_frame(name="Variance") for d in data]


@dataclass
class Skewness(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.skew().to_frame(name="Skewness") for d in data]


@dataclass
class Kurtosis(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.kurt().to_frame(name="Kurtosis") for d in data]


@dataclass
class ZeroCrossing(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:

        def zero_crossing(array: np.ndarray) -> np.ndarray:
            return np.where(np.diff(np.sign(array)))[0].shape[0]

        return [
            d.apply(zero_crossing, raw=True).to_frame(name="Zero Crossing")
            for d in data
        ]


@dataclass
class AbsoluteArea(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:

        def absolute_area(array: np.ndarray) -> np.ndarray:
            return scipy.integrate.simps(np.abs(array), dx=1e-6)

        return [
            d.apply(absolute_area, raw=True).to_frame(name="Absolute Area")
            for d in data
        ]


@dataclass
class PeakToPeak(Preprocessor):
    
    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:

        def pk2pk(array: np.ndarray) -> np.ndarray:
            return np.max(array) - np.min(array)

        return [
            d.apply(pk2pk, raw=True).to_frame(name="Peak To Peak")
            for d in data
        ]
