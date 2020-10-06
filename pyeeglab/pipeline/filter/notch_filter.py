from dataclasses import dataclass

from mne.io import Raw

from ..preprocessor import Preprocessor
from ... import MNE_USE_CUDA


@dataclass
class NotchFilter(Preprocessor):

    frequency: float

    def __call__(self, data: Raw, **kwargs) -> Raw:
        return data.notch_filter(self.frequency, n_jobs=MNE_USE_CUDA)
