from typing import List
import numpy as np

from .tuh_eeg_loader import TUHEEGCorpusLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class TUHEEGCorpusDataset(Dataset):

    def __init__(self, path: str, drop_channels: List[str] = ['IBI', 'BURSTS', 'STI 014'], shift: int = 60, tmax: int = 60) -> None:
        self.loader = TUHEEGCorpusLoader(path)
        self.dataset = self.loader.get_dataset()
        self.labels = [data.label for data in self.dataset]
        self.labels = [0 if label == 'normal' else 1 for label in self.labels]
        self.preprocessor = Preprocessor(
            shift,
            tmax,
            self.get_channels(drop_channels),
            self.loader.get_lowest_frequency()
        )

    def get_channels(self, channels: List[str]) -> List[str]:
        channels = list(set(self.loader.get_channelset()) - set(channels))
        channels = sorted(channels)
        return channels

    def set_bandpass_frequency(self, l_freq: float, h_freq: float) -> None:
        self.preprocessor.set_bandpass_frequency(l_freq, h_freq)

    def load_data(self, frames: int, export: str = None):
        self.preprocessor.set_frames(frames)
        dataset = self.preprocessor.normalize(
            self.dataset,
            self.labels,
            export
        )
        return dataset['data'], dataset['labels']

    def load_frames(self, frames: int, export: str = None):
        self.preprocessor.set_frames(frames)
        dataset = self.preprocessor.get_frames(
            self.dataset,
            self.labels,
            export
        )
        data = np.array(dataset['data']).astype('float32')
        return data, dataset['labels']

    def load_correlations(self, frames: int, export: str = None):
        self.preprocessor.set_frames(frames)
        dataset = self.preprocessor.get_correlations(
            self.dataset,
            self.labels,
            export
        )
        data = np.array(dataset['data']).astype('float32')
        return data['data'], dataset['labels']

    def load_adjs(self, frames: int, c: float, p1: int, p2: int, export: str = None):
        self.preprocessor.set_frames(frames)
        dataset = self.preprocessor.get_adjs(
            self.dataset,
            self.labels,
            c,
            p1,
            p2,
            export
        )
        data = np.array(dataset['data']).astype('float32')
        return data, dataset['labels']

    def load_adjs_no_frames(self, c: float, p1: int, p2: int, export: str = None):
        dataset = self.preprocessor.get_adjs(
            self.dataset,
            self.labels,
            c,
            p1,
            p2,
            export
        )
        data = [d[0] for d in dataset['data']]
        data = np.array(data).astype('float32')
        return data, dataset['labels']

    def load_weighted_adjs(self, frames: int, export: str = None):
        self.preprocessor.set_frames(frames)
        dataset = self.preprocessor.get_weighted_adjs(
            self.dataset,
            self.labels,
            export
        )
        data = np.array(dataset['data']).astype('float32')
        return data, dataset['labels']

    def load_weighted_adjs_no_frames(self, export: str = None):
        dataset = self.preprocessor.get_weighted_adjs(
            self.dataset,
            self.labels,
            export
        )
        data = [d[0] for d in dataset['data']]
        data = np.array(data).astype('float32')
        return data, dataset['labels']

    def load_graphs(self, frames: int, c: float, p1: int, p2: int, node_features: bool, export: str = None):
        self.preprocessor.set_frames(frames)
        dataset = self.preprocessor.get_graphs(
            self.dataset,
            self.labels,
            c,
            p1,
            p2,
            node_features,
            export
        )
        return dataset['data'], dataset['labels']

    def load_graphs_no_frames(self, c: float, p1: int, p2: int, node_features: bool, export: str = None):
        dataset = self.preprocessor.get_graphs(
            self.dataset,
            self.labels,
            c,
            p1,
            p2,
            node_features,
            export
        )
        data = [d[0] for d in dataset['data']]
        return data, dataset['labels']

    def load(self, frames: int, c: float, p1: int, p2: int, export: str = None):
        return self.load_adjs(frames, c, p1, p2, export)
