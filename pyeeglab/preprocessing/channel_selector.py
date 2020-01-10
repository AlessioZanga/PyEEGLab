import logging
from typing import List

from json import dumps

from ..io import Raw
from .pipeline import Preprocessor


class CommonChannelSet(Preprocessor):

    def __init__(self, blacklist: List[str] = []) -> None:
        super().__init__()
        logging.debug('Create common channel_set preprocessor')
        self.blacklist = blacklist

    def to_json(self) -> str:
        json = {
            self.__class__.__name__ : {
                'blacklist': self.blacklist
            }
        }
        json = dumps(json)
        return json

    def run(self, data: Raw, **kwargs) -> Raw:
        channels = set(kwargs['channel_set']) - set(self.blacklist)
        channels = list(channels)
        data.set_channels(channels)
        return data
