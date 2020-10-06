from dataclasses import dataclass

from mne.io import Raw

from ..preprocessor import Preprocessor


@dataclass
class NotchFilter(Preprocessor):

    frequency: float

    def __call__(self, data: Raw, **kwargs) -> Raw:
        return data.notch_filter(self.frequency)
