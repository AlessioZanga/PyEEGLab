import logging

from typing import List

from ...io import DataLoader
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):

    def __init__(self, path: str, exclude_channels_reference: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> None:
        exclude_files = [
            '01_tcp_ar/101/00010158/s001_2013_01_14/00010158_s001_t001.edf',   # Corrupted data
        ]
        super().__init__(path, exclude_channels_reference=exclude_channels_reference, exclude_files=exclude_files)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGArtifactIndex(self.path)
