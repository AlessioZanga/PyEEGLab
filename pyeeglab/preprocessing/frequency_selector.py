import logging

from json import dumps

from ..io import Raw
from .pipeline import Preprocessor


class LowestFrequency(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create lowest_frequency preprocessor')

    def run(self, data: Raw, **kwargs) -> Raw:
        data.set_frequency(kwargs['lowest_frequency'])
        return data
