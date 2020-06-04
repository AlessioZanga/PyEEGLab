import logging

from typing import List

from ...io import DataLoader
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):

    def __init__(self, path: str, exclude_channels_reference: List[str] = ['02_tcp_le', '02_tcp_ar_a']) -> None:
        super().__init__(path, exclude_channels_reference=exclude_channels_reference)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGArtifactIndex(self.path)
