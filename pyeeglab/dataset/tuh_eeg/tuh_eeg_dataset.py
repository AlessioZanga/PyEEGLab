import numpy as np

from .tuh_eeg_loader import TUHEEGCorpusLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class TUHEEGCorpusDataset(Dataset):

    def __init__(self, path):
        self._loader = TUHEEGCorpusLoader(path)

    def _initialize(self, channels):
        self._dataset = self._loader.get_dataset()
        self._labels = [data.label for data in self._dataset]
        self._chs = list(set(self._loader.get_channelset()) - set(channels))
        self._chs = sorted(self._chs)
        self._freq = self._loader.get_lowest_frequency()

    def load_data(self, shift, tmax, channels, l_freq, h_freq, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, frames)
        dataset = self._preprocessor.normalize(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = dataset['data']
        return dataset, labels

    def load_frames(self, shift, tmax, channels, l_freq, h_freq, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, frames)
        dataset = self._preprocessor.get_frames(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels
    
    def load_correlations(self, shift, tmax, channels, l_freq, h_freq, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, frames)
        dataset = self._preprocessor.get_correlations(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def load_adjs(self, shift, tmax, channels, l_freq, h_freq, frames, c, p1, p2, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, frames)
        dataset = self._preprocessor.get_adjs(
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

    def load_adjs_no_frames(self, shift, tmax, channels, l_freq, h_freq, c, p1, p2, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, 0)
        dataset = self._preprocessor.get_adjs(
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

    def load_weighted_adjs(self, shift, tmax, channels, l_freq, h_freq, frames, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, frames)
        dataset = self._preprocessor.get_weighted_adjs(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('float32').reshape((-1, 1))
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels

    def load_weighted_adjs_no_frames(self, shift, tmax, channels, l_freq, h_freq, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, 0)
        dataset = self._preprocessor.get_weighted_adjs(
            self._dataset,
            self._labels,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('int32')
        dataset['data'] = [d[0] for d in dataset['data']]
        dataset = np.array(dataset['data']).astype('float32')
        return dataset, labels
    
    def load_graphs(self, shift, tmax, channels, l_freq, h_freq, frames, c, p1, p2, node_features, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, frames)
        dataset = self._preprocessor.get_graphs(
            self._dataset,
            self._labels,
            c,
            p1,
            p2,
            node_features,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('int32')
        dataset = dataset['data']
        return dataset, labels

    def load_graphs_no_frames(self, shift, tmax, channels, l_freq, h_freq, c, p1, p2, node_features, export=None):
        self._initialize(channels)
        self._preprocessor = Preprocessor(shift, tmax, self._chs, self._freq, l_freq, h_freq, 0)
        dataset = self._preprocessor.get_graphs(
            self._dataset,
            self._labels,
            c,
            p1,
            p2,
            node_features,
            export
        )
        labels = [0 if label == 'normal' else 1 for label in dataset['labels']]
        labels = np.array(labels).astype('int32')
        dataset = [d[0] for d in dataset['data']]
        return dataset, labels

    def load(self, shift, tmax, channels, l_freq, h_freq, frames, c, p1, p2, export=None):
        return self.load_adjs(shift, tmax, channels, l_freq, h_freq, frames, c, p1, p2, export)
