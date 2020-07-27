from typing import Dict

from .tuh_eeg_artifact_loader import TUHEEGArtifactLoader
from ..dataset import Dataset


class TUHEEGArtifactDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_artifact/v2.0.0/edf/') -> None:
        super().__init__(TUHEEGArtifactLoader(path))
    
    def _get_dataset_env(self) -> Dict:
        env = super()._get_dataset_env()
        env['class_id'] = 'bckg'
        return env
