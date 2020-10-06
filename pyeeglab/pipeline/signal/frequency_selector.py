from dataclasses import dataclass

from mne.io import Raw

from ..preprocessor import Preprocessor


@dataclass
class LowestFrequency(Preprocessor):

    def __call__(self, data: Raw, **kwargs) -> Raw:
        lowest_frequency = kwargs["lowest_frequency"]
        if data.info["sfreq"] > lowest_frequency:
            data = data.resample(lowest_frequency)
        return data
