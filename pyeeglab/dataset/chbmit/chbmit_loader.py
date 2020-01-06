import logging

from typing import List

from ...io import DataLoader
from .chbmit_index import CHBMITIndex


class CHBMITLoader(DataLoader):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        logging.debug('Create CHB-MIT Scalp EEG Loader')
        self.index = CHBMITIndex(self.path)
