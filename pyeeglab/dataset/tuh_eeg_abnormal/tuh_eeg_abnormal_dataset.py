from typing import Dict

from .tuh_eeg_abnormal_loader import TUHEEGAbnormalLoader
from ..dataset import Dataset


class TUHEEGAbnormalDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_abnormal/v2.0.0/edf/') -> None:
        super().__init__(TUHEEGAbnormalLoader(path))

    def _get_dataset_env(self) -> Dict:
        blacklist = ['IBI', 'BURSTS', 'STI 014', 'SUPPR']
        channel_set = self.loader.get_channelset()
        channel_set = set(channel_set) - set(blacklist)
        channel_set = list(channel_set)
        return {
            'channel_set': channel_set,
            'lowest_frequency': self.loader.get_lowest_frequency()
        }
