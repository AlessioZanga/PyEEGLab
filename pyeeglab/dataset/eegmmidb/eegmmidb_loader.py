import logging

from typing import List

from ...io import DataLoader
from .eegmmidb_index import EEGMMIDBIndex


class EEGMMIDBLoader(DataLoader):

    def __init__(self, path: str, exclude_frequency: List[int] = [128]) -> None:
        super().__init__(path, exclude_frequency = exclude_frequency)
        logging.debug('Create EEG Motor Movement/Imagery Loader')
        self.index = EEGMMIDBIndex(self.path)
