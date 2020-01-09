import logging

from json import dumps

from ..io import Raw
from .pipeline import Preprocessor


class CommonChannelSet(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create common channel_set preprocessor')

    def to_json(self) -> str:
        json = {self.__class__.__name__ : {}}
        json = dumps(json)
        return json

    def run(self, data: Raw, **kwargs) -> Raw:
        data.set_channels(kwargs['channel_set'])
        return data
