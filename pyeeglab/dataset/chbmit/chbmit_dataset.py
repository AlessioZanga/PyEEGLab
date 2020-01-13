from .chbmit_loader import CHBMITLoader
from ..dataset import Dataset


class CHBMITDataset(Dataset):

    def __init__(self, path: str = './data/physionet.org/files/chbmit/1.0.0/') -> None:
        super().__init__(CHBMITLoader(path))
