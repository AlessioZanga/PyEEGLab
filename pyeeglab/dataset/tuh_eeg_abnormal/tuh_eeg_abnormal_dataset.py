from .tuh_eeg_abnormal_loader import TUHEEGAbnormalLoader
from ..dataset import Dataset


class TUHEEGAbnormalDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_abnormal/v2.0.0/edf/') -> None:
        self.loader = TUHEEGAbnormalLoader(path)
