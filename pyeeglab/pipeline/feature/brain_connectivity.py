from dataclasses import dataclass
from itertools import product

from typing import List

import numpy as np
import pandas as pd
import yasa

from ..preprocessor import Preprocessor


@dataclass
class SpearmanCorrelation(Preprocessor):

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        return [d.corr(method="spearman").rename_axis(None) for d in data]


@dataclass
class BinarizedSpearmanCorrelation(SpearmanCorrelation):

    c: float = 0.75
    p1: float = 0.25
    p2: float = 0.75

    def _binarize_item(self, item: float, p1: float, p2: float, err: float = 0.01) -> bool:
        if item <= np.min([-self.c, p1])*(1+err) or item >= np.max([+self.c, p2])*(1-err):
            return True
        return False

    def _binarize_dataset(self, dataframe: pd.DataFrame, perc: np.ndarray) -> pd.DataFrame:
        shape = dataframe.shape
        shape = product(*[range(s) for s in shape])
        for i, j in shape:
            dataframe.iloc[i, j] = self._binarize_item(
                dataframe.iloc[i, j],
                perc[0][i][j],
                perc[1][i][j]
            )
        return dataframe

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        data = super().__call__(data, **kwargs)
        perc = np.array([d.to_numpy() for d in data])
        perc = np.percentile(perc, (self.p1, self.p2), axis=0)
        for index, value in enumerate(data):
            data[index] = self._binarize_dataset(value, perc)
        return data


@dataclass
class BandPower(Preprocessor):

    bands: List[str] = tuple(["Delta", "Theta", "Alpha", "Beta", "Gamma"])

    def __call__(self, data: List[pd.DataFrame], **kwargs) -> List[pd.DataFrame]:
        data = [d.swapaxes("index", "columns") for d in data]
        data = [
            yasa.bandpower(d.to_numpy(), kwargs["lowest_frequency"], d.index)
            for d in data
        ]
        data = [d.loc[:, self.bands] for d in data]
        return data
