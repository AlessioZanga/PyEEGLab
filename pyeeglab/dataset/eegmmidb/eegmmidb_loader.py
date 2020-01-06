import logging

from ...io import DataLoader
from .eegmmidb_index import EEGMMIDBIndex


class EEGMMIDBLoader(DataLoader):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        logging.debug('Create EEG Motor Movement/Imagery Loader')
        self.index = EEGMMIDBIndex(self.path)
