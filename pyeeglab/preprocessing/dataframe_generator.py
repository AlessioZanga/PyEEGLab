import logging

from json import dumps
from pandas import DataFrame

from ..io import Raw
from .pipeline import Preprocessor


class ToDataframe(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create dataframe generator preprocessor')

    def to_json(self) -> str:
        json = {self.__class__.__name__ : {}}
        json = dumps(json)
        return json

    def run(self, data: Raw, **kwargs) -> DataFrame:
        dataframe = data.open().to_data_frame()
        return dataframe
