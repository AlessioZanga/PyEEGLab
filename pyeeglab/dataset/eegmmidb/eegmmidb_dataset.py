from .eegmmidb_loader import EEGMMIDBLoader
from ..dataset import Dataset


class EEGMMIDBDataset(Dataset):

    def __init__(self, path: str = './data/physionet.org/files/eegmmidb/1.0.0/') -> None:
        super().__init__(EEGMMIDBLoader(path))
