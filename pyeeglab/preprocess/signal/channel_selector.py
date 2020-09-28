import json
import logging

from typing import List

from mne.io import Raw

from ...pipeline import Preprocessor

class CommonChannelSet(Preprocessor):

    def __init__(self, blacklist: List[str] = None) -> None:
        super().__init__()
        logging.debug('Create common channels_set preprocessor')
        self.blacklist = blacklist if blacklist else []

    def to_json(self) -> str:
        out = {
            self.__class__.__name__ : {
                'blacklist': self.blacklist
            }
        }
        out = json.dumps(out)
        return out

    def run(self, data: Raw, **kwargs) -> Raw:
        channels = set(data.ch_names)
        channels = channels.difference(set(kwargs['channels_set']))
        data = data.drop_channels(channels)
        data = data.drop_channels(self.blacklist)
        data = data.reorder_channels(kwargs['channels_set'])
        return data
