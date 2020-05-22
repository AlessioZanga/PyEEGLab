import logging

from json import dumps
from numpy import ndarray,max, min
from pandas import DataFrame
from typing import List

from .pipeline import Preprocessor

class MinMaxNormalization(Preprocessor):
    def run(self, data: DataFrame, **kwargs) -> DataFrame:
        
        def min_max_norm(array: ndarray) -> ndarray:
            return (array - min(array))/(max(array) - min(array))

        return data.apply(min_max_norm, raw=True)
