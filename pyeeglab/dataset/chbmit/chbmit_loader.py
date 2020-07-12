import logging

from typing import List

from ...io import DataLoader
from .chbmit_index import CHBMITIndex


class CHBMITLoader(DataLoader):

    def __init__(self, path: str) -> None:
        exclude_files = [
            'chb03/chb03_35.edf',   # Corrupted data
            'chb12/chb12_27.edf',   # Bad channel names
            'chb12/chb12_28.edf',   # Bad channel names
            'chb12/chb12_29.edf',   # Bad channel names
        ]
        super().__init__(path, exclude_files=exclude_files)
        logging.debug('Create CHB-MIT Scalp EEG Loader')
        self.index = CHBMITIndex(self.path)
