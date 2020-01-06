import logging

from typing import List

from ...io import DataLoader, Raw
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        logging.debug('Create TUH EEG Corpus Loader')
        self.index = TUHEEGArtifactIndex(self.path)

    def get_dataset(self, ext: str = 'edf', exclude_channel_ref: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> List[Raw]:
        return super().get_dataset(ext, exclude_channel_ref)

    def get_channelset(self, exclude_channel_ref: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> List[str]:
        return super().get_channelset(exclude_channel_ref)
