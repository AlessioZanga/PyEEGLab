from .tuh_eeg_artifact_loader import TUHEEGArtifactLoader
from ..dataset import Dataset


class TUHEEGArtifactDataset(Dataset):

    def __init__(self, path: str = './data/tuh_eeg_artifact/v1.0.0/edf/') -> None:
        super().__init__(TUHEEGArtifactLoader(path))
