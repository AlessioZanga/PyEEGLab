import logging
import json

from ...io import Raw
from ...pipeline import Preprocessor


class BandPassFrequency(Preprocessor):

    def __init__(self, low_freq: float, high_freq: float) -> None:
        super().__init__()
        self.low_freq = low_freq
        self.high_freq = high_freq
        logging.debug('Create band pass filter (%f Hz, %f Hz) preprocessor', low_freq, high_freq)

    def to_json(self) -> str:
        out = {
            self.__class__.__name__ : {
                'low_freq': self.low_freq,
                'high_freq': self.high_freq
            }
        }
        out = json.dumps(out)
        return out

    def run(self, data: Raw, **kwargs) -> Raw:
        data.set_filter(self.low_freq, self.high_freq)
        return data


class NotchFrequency(Preprocessor):

    def __init__(self, freq: float) -> None:
        super().__init__()
        self.freq = freq
        logging.debug('Create notch filter %f Hz preprocessor', freq)

    def to_json(self) -> str:
        out = {
            self.__class__.__name__ : {
                'freq': self.freq
            }
        }
        out = json.dumps(out)
        return out

    def run(self, data: Raw, **kwargs) -> Raw:
        data.notch_filter(self.freq)
        return data
