import numpy as np

from .tuh_eeg_loader import TUHEEGCorpusLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class TUHEEGCorpusDataset(Dataset):

    def __init__(self, path):
        self._loader = TUHEEGCorpusLoader(path)

    def _initialize(self, channels):
        self._dataset = self._loader.getDataset()
        self._labels = [data.label() for data in self._dataset]
        self._chs = list(set(self._loader.getChannelSet()) - set(channels))
        self._chs = sorted(self._chs)
        self._freq = self._loader.getLowestFrequency()

    def loadData(self, shift, tmax, channels, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, frames)
        dataset = self._preprocessor.normalize(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = dataset['data']
        return dataset, labels

    def loadFrames(self, shift, tmax, channels, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, frames)
        dataset = self._preprocessor.getFrames(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def loadAdjs(self, shift, tmax, channels, frames, c, p1, p2, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, frames)
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

    def loadAdjsNoFrames(self, shift, tmax, channels, c, p1, p2, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, 0)
        dataset = self._preprocessor.getAdjs(
            self._dataset,
            self._labels,
            c,
            p1,
            p2,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('int32')
        dataset['data'] = [d[0] for d in dataset['data']]
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def loadWeightedAdjs(self, shift, tmax, channels, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, frames)
        dataset = self._preprocessor.getWeightedAdjs(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def loadWeightedAdjsNoFrames(self, shift, tmax, channels, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, 0)
        dataset = self._preprocessor.getWeightedAdjs(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('int32')
        dataset['data'] = [d[0] for d in dataset['data']]
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def loadGraphsNoFrames(self, shift, tmax, channels, c, p1, p2, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, 0)
        dataset = self._preprocessor.getGraphs(
            self._dataset,
            self._labels,
            c,
            p1,
            p2,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('int32')
        dataset = [d[0] for d in dataset['data']]
        return dataset, labels

    def load(self, shift, tmax, channels, frames, c, p1, p2, export=None):
        return self.loadAdjs(shift, tmax, channels, frames, c, p1, p2, export)
