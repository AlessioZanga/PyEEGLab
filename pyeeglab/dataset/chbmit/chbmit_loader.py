import logging

from typing import List

from ...io import DataLoader
from .chbmit_index import CHBMITIndex


class CHBMITLoader(DataLoader):

    def __init__(self, path: str) -> None:
        # Excluding files with bad channels name
        exclude_files = [
            'chb12/chb12_27.edf',
            'chb12/chb12_28.edf',
            'chb12/chb12_29.edf'
        ]
        super().__init__(path, exclude_files=exclude_files)
        logging.debug('Create CHB-MIT Scalp EEG Loader')
        self.index = CHBMITIndex(self.path)
