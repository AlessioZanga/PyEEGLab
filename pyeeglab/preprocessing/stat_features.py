import logging

from json import dumps
from numpy import ndarray, abs, where, diff, sign, max, min
from scipy.integrate import simps
from pandas import DataFrame
from typing import List

from .pipeline import Preprocessor


class Mean(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        return [d.mean().to_frame(name='Mean') for d in data]


class Variance(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        return [d.var().to_frame(name='Variance') for d in data]


class Skewness(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        return [d.skew().to_frame(name='Skewness') for d in data]


class Kurtosis(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        return [d.kurt().to_frame(name='Kurtosis') for d in data]


class ZeroCrossing(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        
        def zero_crossing(array: ndarray) -> ndarray:
            return where(diff(sign(array)))[0].shape[0]

        return [d.apply(zero_crossing, raw=True).to_frame(name='Zero Crossing') for d in data]


class AbsoluteArea(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        
        def absolute_area(array: ndarray) -> ndarray:
            return simps(abs(array), dx=1e-6)

        return [d.apply(absolute_area, raw=True).to_frame(name='Absolute Area') for d in data]


class PeakToPeak(Preprocessor):
    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        
        def pk2pk(array: ndarray) -> ndarray:
            return max(array) - min(array)

        return [d.apply(pk2pk, raw=True).to_frame(name='Peak To Peak') for d in data]
