import numpy as np

from .tuh_eeg_loader import TUHEEGCorpusLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class TUHEEGCorpusDataset(Dataset):

    def __init__(self, path):
        self._loader = TUHEEGCorpusLoader(path)

    def loadData(self, tmax, channels, frames, export=None):
        self._dataset = self._loader.getDataset()
        self._labels = [data.label() for data in self._dataset]
        channels = list(set(self._loader.getChannelSet()) - set(channels))
        channels = sorted(channels)
        frequency = self._loader.getLowestFrequency()
        self._preprocessor = Preprocessor(tmax, channels, frequency, frames)
        dataset = self._preprocessor.normalize(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def loadFrames(self, tmax, channels, frames, export=None):
        self._dataset = self._loader.getDataset()
        self._labels = [data.label() for data in self._dataset]
        channels = list(set(self._loader.getChannelSet()) - set(channels))
        channels = sorted(channels)
        frequency = self._loader.getLowestFrequency()
        self._preprocessor = Preprocessor(tmax, channels, frequency, frames)
        dataset = self._preprocessor.getFrames(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def loadAdjs(self, tmax, channels, frames, c, p1, p2, export=None):
        self._dataset = self._loader.getDataset()
        self._labels = [data.label() for data in self._dataset]
        channels = list(set(self._loader.getChannelSet()) - set(channels))
        channels = sorted(channels)
        frequency = self._loader.getLowestFrequency()
        self._preprocessor = Preprocessor(tmax, channels, frequency, frames)
        dataset = self._preprocessor.getAdjs(
            self._dataset,
            self._labels,
            c,
            p1,
            p2,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels
