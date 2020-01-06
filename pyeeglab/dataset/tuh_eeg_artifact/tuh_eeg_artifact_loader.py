import logging

from typing import List

from ...io import DataLoader
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):

    def __init__(self, path: str, exclude_channel_ref: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> None:
        super().__init__(path, exclude_channel_ref = exclude_channel_ref)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGArtifactIndex(self.path)
