from typing import Dict

from .tuh_eeg_seizure_loader import TUHEEGSeizureLoader
from ..dataset import Dataset


class TUHEEGSeizureDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_seizure/v1.5.2/edf/') -> None:
        super().__init__(TUHEEGSeizureLoader(path))
    
    def _get_dataset_env(self) -> Dict:
        env = super()._get_dataset_env()
        env['class_id'] = 'fnsz'
        return env
