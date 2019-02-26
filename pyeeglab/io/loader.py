import logging
from abc import ABC, abstractmethod

import mne


class DataLoader(ABC):
    _index = None
    _logger = logging.getLogger()

    def __init__(self):
        self._logger.debug('Create data loader')

    def index(self):
        return self._index

    @abstractmethod
    def getTrainSet(self):
        pass

    @abstractmethod
    def getTestSet(self):
        pass

    @abstractmethod
    def getEDFSet(self):
        pass

    @abstractmethod
    def getEDFSetByFrequency(self, frequency=250):
        pass

    @abstractmethod
    def getChannelSet(self):
        pass

    @abstractmethod
    def getLowestFrequency(self):
        pass


class EDFLoader():
    _id = None
    _path = None
    _reader = None
    _logger = logging.getLogger()

    def __init__(self, id, path):
        self._id = id
        self._path = path
        self._logger.debug('Create EDFLoader %s', self._id)

    def path(self):
        return self._path

    def open(self):
        if self._reader is None:
            self._logger.debug('Open EDFLoader %s reader', self._id)
            self._reader = mne.io.read_raw_edf(self.path())
        return self._reader

    def close(self):
        if self._reader is not None:
            self._logger.debug('Close EDFLoader %s reader', self._id)
            self._reader.close()
        self._reader = None

    def reader(self):
        return self.open()

    def getId(self):
        return self._id

    def setTMax(self, tmax):
        self._logger.debug('Crop EDFLoader %s data to %s seconds', self.getId(), tmax)
        self.reader().crop(0, tmax)

    def setChannels(self, channels=[]):
        channels = set(self.reader().ch_names) - set(channels)
        self._logger.debug(
            'Set EDFLoader %s channels drop %s', self.getId(), '|'.join(channels)
        )
        self.reader().drop_channels(list(channels))

    def exportCSV(self, path=None):
        if path is None:
            suffix = '.edf'
            if self.path().endswith(suffix):
                path = self.path()[:-len(suffix)] + '.csv'
        self._logger.debug('Export EDFLoader %s to CSV scaling EEG by 1E6', self.getId())
        self.reader().to_data_frame().to_csv(path)
