import logging
import json

from ...io import Raw
from ...pipeline import Preprocessor

from typing import List


class CommonChannelSet(Preprocessor):

    def __init__(self, blacklist: List[str] = []) -> None:
        super().__init__()
        logging.debug('Create common channels_set preprocessor')
        self.blacklist = blacklist

    def to_json(self) -> str:
        out = {
            self.__class__.__name__ : {
                'blacklist': self.blacklist
            }
        }
        out = json.dumps(out)
        return out

    def run(self, data: Raw, **kwargs) -> Raw:
        channels = set(kwargs['channels_set']) - set(self.blacklist)
        channels = list(channels)
        data.set_channels(channels)
        return data
