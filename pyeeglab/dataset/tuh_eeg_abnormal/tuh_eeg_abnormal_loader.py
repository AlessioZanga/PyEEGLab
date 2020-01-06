import logging

from ...io import DataLoader
from .tuh_eeg_abnormal_index import TUHEEGAbnormalIndex


class TUHEEGAbnormalLoader(DataLoader):

    def __init__(self, path: str) -> None:
        super().__init__(path)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGAbnormalIndex(self.path)
