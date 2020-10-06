from dataclasses import dataclass

from typing import List

from mne.io import Raw

from ..preprocessor import Preprocessor


@dataclass
class CommonChannelSet(Preprocessor):

    blacklist: List[str] = None

    def __call__(self, data: Raw, **kwargs) -> Raw:
        channels = set(data.ch_names)
        channels = channels.difference(set(kwargs["channels_set"]))
        data = data.drop_channels(channels)
        # Check if blacklist has been initialized
        if self.blacklist:
            data = data.drop_channels(self.blacklist)
        return data.reorder_channels(kwargs["channels_set"])
