from typing import List

from .tuh_eeg_abnormal_loader import TUHEEGAbnormalLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class TUHEEGAbnormalDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_abnormal/v2.0.0/edf/', drop_channels: List[str] = ['IBI', 'BURSTS', 'STI 014'], frames: int = 8) -> None:
        super().__init__()
        self.loader = TUHEEGAbnormalLoader(path)
        self.dataset = self.loader.get_dataset()
        self.labels = [data.label for data in self.dataset]
        self.labels = [0 if label == 'normal' else 1 for label in self.labels]
        self.preprocessor = Preprocessor(
            self.get_channels(drop_channels),
            self.loader.get_lowest_frequency(),
            frames
        )
