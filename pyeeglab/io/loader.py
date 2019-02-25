from abc import ABC, abstractmethod

import mne


class DataLoader(ABC):
    _index = None

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


class EDFLoader():
    _id = None
    _path = None
    _reader = None

    def __init__(self, id, path):
        self._id = id
        self._path = path

    def path(self):
        return self._path

    def open(self):
        if self._reader is None:
            self._reader = mne.io.read_raw_edf(self.path())
        return self._reader

    def close(self):
        if self._reader is not None:
            self._reader.close()
        self._reader = None

    def reader(self):
        return self.open()

    def getId(self):
        return self._id

    def setChannels(self, channels=[]):
        channels = set(self.reader().ch_names) - set(channels)
        self.reader().drop_channels(list(channels))
