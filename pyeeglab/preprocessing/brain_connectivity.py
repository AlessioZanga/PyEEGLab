import logging
from typing import List

from json import dumps
from pandas import DataFrame

from .pipeline import Preprocessor


class SpearmanCorrelation(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create spearman correlation preprocessor')

    def to_json(self) -> str:
        json = {self.__class__.__name__ : {}}
        json = dumps(json)
        return json

    def run(self, data: List[DataFrame], **kwargs) -> List[DataFrame]:
        data = [d.corr(method='spearman') for d in data]
        return data
