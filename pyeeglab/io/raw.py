import logging
from abc import ABC, abstractmethod
from typing import List
from importlib.util import find_spec
import mne

class Raw(ABC):
    _reader = None

    def __init__(self, fid: str, path: str, label: str) -> None:
        self.id = fid
        self.path = path
        self.label = label

    @abstractmethod
    def close(self) -> None:
        pass

    @abstractmethod
    def crop(self, offset: int, length: int) -> None:
        pass

    @abstractmethod
    def open(self) -> mne.io.Raw:
        pass

    @abstractmethod
    def get_annotations(self):
        pass

    @abstractmethod
    def set_channels(self, channels: List[str]) -> None:
        pass

    @abstractmethod
    def set_frequency(self, frequency: float, low_freq: float = 0, high_freq: float = 0) -> None:
        pass


class RawEDF(Raw):

    def __init__(self, fid: str, path: str, label: str) -> None:
        super().__init__(fid, path, label)

    def close(self) -> None:
        if self._reader is not None:
            logging.debug('Close RawEDF %s reader', self.id)
            self._reader.close()
        self._reader = None

    def crop(self, offset: int, length: int) -> None:
        logging.debug('Crop RawEDF %s data to %s seconds from %s', self.id, length, offset)
        self.open().crop(offset, offset + length)

    def open(self) -> mne.io.Raw:
        if self._reader is None:
            logging.debug('Open RawEDF %s reader', self.id)
            try:
                self._reader = mne.io.read_raw_edf(self.path)
            except RuntimeError:
                logging.debug('Using preload for RawEDF %s reader', self.id)
                self._reader = mne.io.read_raw_edf(self.path, preload=True)
        return self._reader

    def get_annotations(self):
        annotations = self.open().annotations
        annotations = list(zip(annotations.onset, annotations.durations))
        keys = ['begin', 'end']
        annotations = dict([zip(keys, a) for a in annotations])
        return annotations

    def set_channels(self, channels: List[str]) -> None:
        channels = set(self.open().ch_names) - set(channels)
        logging.debug('Set RawEDF %s channels drop %s', self.id, '|'.join(channels))
        self.open().drop_channels(list(channels))

    def set_frequency(self, frequency: float, low_freq: float = 0, high_freq: float = 0) -> None:
        sfreq = self.open().info['sfreq']
        if sfreq > frequency:
            logging.debug('Downsample %s from %s to %s', self.id, sfreq, frequency)
        n_jobs = 1
        if find_spec('cupy') is not None:
            logging.debug('Load CUDA Cores for processing %s', self.id)
            n_jobs = 'cuda'
        if low_freq > 0 and high_freq > 0:
            self.open().filter(low_freq, high_freq, n_jobs=n_jobs)
        self.open().resample(frequency, n_jobs=n_jobs)
