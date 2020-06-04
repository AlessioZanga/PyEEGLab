from typing import Dict

from .tuh_eeg_abnormal_loader import TUHEEGAbnormalLoader
from ..dataset import Dataset


class TUHEEGAbnormalDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_abnormal/v2.0.0/edf/') -> None:
        super().__init__(TUHEEGAbnormalLoader(path))

    def _get_dataset_env(self) -> Dict:
        env = super()._get_dataset_env()
        blacklist = ['IBI', 'BURSTS', 'STI 014', 'SUPPR']
        env['channels_set'] = list(set(env['channels_set']) - set(blacklist))
        return env
