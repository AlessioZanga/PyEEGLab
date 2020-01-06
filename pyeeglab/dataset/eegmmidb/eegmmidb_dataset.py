from typing import List
import numpy as np

from .eegmmidb_loader import EEGMMIDBLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class EEGMMIDBDataset(Dataset):

    def __init__(self, path: str, frames: int = 8) -> None:
        self.loader = EEGMMIDBLoader(path)
        self.dataset = self.loader.get_dataset()
        self.labels = [data.label for data in self.dataset]
        onehot_encoder = sorted(set(self.labels))
        self.labels = [onehot_encoder.index(label) for label in self.labels]
        self.preprocessor = Preprocessor(
            self.get_channels([]),
            self.loader.get_lowest_frequency(),
            frames
        )

    def get_channels(self, drop_channels: List[str]) -> List[str]:
        channels = list(set(self.loader.get_channelset()) - set(drop_channels))
        channels = sorted(channels)
        return channels

    def set_bandpass_frequency(self, l_freq: float, h_freq: float) -> None:
        self.preprocessor.set_bandpass_frequency(l_freq, h_freq)

    # Modes: frames, correlations, adjs, weighted_adjs, graphs

    def load(self, mode: str = 'adjs', c: float = 0.7, p1: int = 25, p2: int = 75, node_features: bool = False, export: str = None):
        dataset = self.preprocessor.load(
            mode,
            self.dataset,
            self.labels,
            c,
            p1,
            p2,
            node_features,
            export
        )
        data = dataset['data']
        labels = dataset['labels']
        if mode != 'graphs':
            data = np.array(data).astype('float32')
        labels = np.array(labels).astype('int32')
        return data, labels
