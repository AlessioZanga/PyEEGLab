from typing import List

from .tuh_eeg_artifact_loader import TUHEEGArtifactLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class TUHEEGArtifactDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_artifact/v1.0.0/edf/', drop_channels: List[str] = ['IBI', 'BURSTS', 'STI 014'], frames: int = 8) -> None:
        super().__init__()
        self.loader = TUHEEGArtifactLoader(path)
        self.dataset = self.loader.get_dataset()
        self.labels = [data.label for data in self.dataset]
        onehot_encoder = sorted(set(self.labels))
        self.labels = [onehot_encoder.index(label) for label in self.labels]
        self.preprocessor = Preprocessor(
            self.get_channels(drop_channels),
            self.loader.get_lowest_frequency(),
            frames
        )
