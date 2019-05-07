import logging
from abc import ABC, abstractmethod

import mne


class Raw(ABC):
    _reader = None
    _logger = logging.getLogger()

    def __init__(self, id, path, label):
        self._id = id
        self._path = path
        self._label = label

    def id(self):
        return self._id

    def path(self):
        return self._path

    def label(self):
        return self._label

    @abstractmethod
    def open(self):
        pass

    @abstractmethod
    def close(self):
        pass

    @abstractmethod
    def reader(self):
        pass

    @abstractmethod
    def setTMax(self, tmax, shift):
        pass

    @abstractmethod
    def setChannels(self, channels):
        pass


class RawEDF(Raw):

    def __init__(self, id, path, label):
        super().__init__(id, path, label)
        # self._logger.debug('Create RawEDF %s', self._id)

    def open(self):
        if self._reader is None:
            self._logger.debug('Open RawEDF %s reader', self._id)
            self._reader = mne.io.read_raw_edf(self.path())
        return self._reader

    def close(self):
        if self._reader is not None:
            self._logger.debug('Close RawEDF %s reader', self._id)
            self._reader.close()
        self._reader = None

    def reader(self):
        return self.open()

    def setTMax(self, tmax, shift):
        self._logger.debug('Crop RawEDF %s data to %s seconds', self.id(), tmax)
        self.reader().crop(shift, shift+tmax)

    def setChannels(self, channels):
        channels = set(self.reader().ch_names) - set(channels)
        self._logger.debug(
            'Set RawEDF %s channels drop %s', self.id(), '|'.join(channels)
        )
        self.reader().drop_channels(list(channels))
