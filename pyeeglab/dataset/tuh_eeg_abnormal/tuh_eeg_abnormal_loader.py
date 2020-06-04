import logging

from ...io import DataLoader
from .tuh_eeg_abnormal_index import TUHEEGAbnormalIndex

from typing import List


class TUHEEGAbnormalLoader(DataLoader):

    def __init__(self, path: str, exclude_channels_reference: List[str] = ['02_tcp_le', '02_tcp_ar_a']) -> None:
        super().__init__(path, exclude_channels_reference=exclude_channels_reference)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGAbnormalIndex(self.path)
