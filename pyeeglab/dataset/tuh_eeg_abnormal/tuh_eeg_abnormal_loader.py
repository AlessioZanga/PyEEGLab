import logging

from os.path import join, sep
from typing import List
from ...database import File
from ...io import DataLoader, RawEDF
from .tuh_eeg_abnormal_index import TUHEEGAbnormalIndex


class TUHEEGAbnormalLoader(DataLoader):
    def __init__(self, path: str) -> None:
        super().__init__()
        logging.debug('Create TUH EEG Corpus Loader')
        if path[-1] != sep:
            path = path + sep
        self.index = TUHEEGAbnormalIndex(path)

    def get_dataset(self) -> List[RawEDF]:
        edfs = self.index.db.query(File).filter(
            File.format == 'edf'
        ).all()
        edfs = [
            RawEDF(f.id, join(self.index.path, f.path), f.label)
            for f in edfs
        ]
        return edfs
