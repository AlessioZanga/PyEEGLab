from dataclasses import dataclass

from mne.io import Raw

from ..preprocessor import Preprocessor
from ... import MNE_USE_CUDA


@dataclass
class BandPassFilter(Preprocessor):

    low_frequency: float
    high_frequency: float

    def __call__(self, data: Raw, **kwargs) -> Raw:
        return data.filter(self.low_frequency, self.high_frequency, n_jobs=MNE_USE_CUDA)
