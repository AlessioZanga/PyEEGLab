from .chbmit_loader import CHBMITLoader
from ..dataset import Dataset
from ...preprocessing import Preprocessor


class CHBMITDataset(Dataset):

    def __init__(self, path: str = './data/physionet.org/files/chbmit/1.0.0/', frames: int = 8) -> None:
        super().__init__()
        self.loader = CHBMITLoader(path)
        self.dataset = self.loader.get_dataset()
        self.labels = [data.label for data in self.dataset]
        onehot_encoder = sorted(set(self.labels))
        self.labels = [onehot_encoder.index(label) for label in self.labels]
        self.preprocessor = Preprocessor(
            self.get_channels([]),
            self.loader.get_lowest_frequency(),
            frames
        )
