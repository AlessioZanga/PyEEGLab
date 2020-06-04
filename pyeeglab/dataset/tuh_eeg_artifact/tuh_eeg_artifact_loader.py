import logging

from typing import List

from ...io import DataLoader
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGArtifactIndex(self.path)
