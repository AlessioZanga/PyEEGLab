from typing import Dict

from .chbmit_loader import CHBMITLoader
from ..dataset import Dataset


class CHBMITDataset(Dataset):

    def __init__(self, path: str = './data/physionet.org/files/chbmit/1.0.0/') -> None:
        super().__init__(CHBMITLoader(path))
    
    def _get_dataset_env(self) -> Dict:
        env = super()._get_dataset_env()
        env['class_id'] = 'noseizure'
        return env
