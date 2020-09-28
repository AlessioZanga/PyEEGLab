import logging

from mne.io import Raw

from ...pipeline import Preprocessor


class LowestFrequency(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create lowest_frequency preprocessor')

    def run(self, data: Raw, **kwargs) -> Raw:
        lowest_frequency = kwargs['lowest_frequency']
        if data.info['sfreq'] > lowest_frequency:
            data = data.resample(lowest_frequency)
        return data
