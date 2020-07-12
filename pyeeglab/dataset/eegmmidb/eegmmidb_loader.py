import logging

from typing import List

from ...io import DataLoader
from .eegmmidb_index import EEGMMIDBIndex


class EEGMMIDBLoader(DataLoader):

    def __init__(self, path: str, exclude_frequency: List[int] = [128]) -> None:
        exclude_files = [
            'S021/S021R08.edf',     # Corrupted data
            'S104/S104R04.edf',     # Corrupted data
        ]
        super().__init__(path, exclude_files = exclude_files, exclude_frequency = exclude_frequency)
        logging.debug('Create EEG Motor Movement/Imagery Loader')
        self.index = EEGMMIDBIndex(self.path)
