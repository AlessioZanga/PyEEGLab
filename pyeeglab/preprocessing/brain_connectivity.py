import logging
from typing import List

from json import dumps
from yasa import bandpower
from numpy import array, ndarray, percentile
from pandas import DataFrame
from itertools import product

from .pipeline import Preprocessor


class SpearmanCorrelation(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create spearman correlation preprocessor')

    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        return [d.corr(method='spearman').rename_axis(None) for d in data]


class BinarizedSpearmanCorrelation(SpearmanCorrelation):

    def __init__(self, c: float = 0.75, p1: float = 0.25, p2: float = 0.75) -> None:
        super().__init__()
        logging.debug('Create binarized (%.4f, %.4f, %.4f) spearman correlation preprocessor', c, p1, p2)
        self.c = c
        self.p1 = p1
        self.p2 = p2

    def to_json(self) -> str:
        json = {
            self.__class__.__name__ : {
                'c': self.c,
                'p1': self.p1,
                'p2': self.p2
            }
        }
        json = dumps(json)
        return json

    def _binarize_item(self, item: float, p1: float, p2: float, err: float = 0.01) -> bool:
        if item <= min([-self.c, p1])*(1+err) or item >= max([+self.c, p2])*(1-err):
            return True
        return False

    def _binarize_dataset(self, dataframe: DataFrame, perc: ndarray) -> DataFrame:
        shape = dataframe.shape
        shape = product(*[range(s) for s in shape])
        for i, j in shape:
            dataframe.iloc[i, j] = self._binarize_item(
                dataframe.iloc[i, j],
                perc[0][i][j],
                perc[1][i][j]
            )
        return dataframe

    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        data = super().run(data, **kwargs)
        perc = array([d.to_numpy() for d in data])
        perc = percentile(perc, (self.p1, self.p2), axis=0)
        for index, value in enumerate(data):
            data[index] = self._binarize_dataset(value, perc)
        return data


class Bandpower(Preprocessor):

    def __init__(self, bands: List[str] = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']) -> None:
        super().__init__()
        logging.debug('Create bandpower (%s) preprocessor', ','.join(bands))
        self.bands = bands

    def to_json(self) -> str:
        json = {
            self.__class__.__name__ : {
                'bands': self.bands,
            }
        }
        json = dumps(json)
        return json

    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        data = [d.swapaxes('index', 'columns') for d in data]
        data = [
            bandpower(d.to_numpy(), kwargs['lowest_frequency'], d.index)
            for d in data
        ]
        data = [d.loc[:, self.bands] for d in data]
        return data
