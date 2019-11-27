import json
import logging

from os.path import join, sep
from typing import List, Dict
from sqlalchemy import func
from ...database.index import File, Metadata
from ...io.loader import DataLoader
from ...io.raw import RawEDF
from .tuh_eeg_abnormal_index import TUHEEGAbnormalIndex


class TUHEEGAbnormalLoader(DataLoader):
    def __init__(self, path: str) -> None:
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

    def get_dataset_text(self) -> Dict:
        txts = self.index.db.query(File).filter(
            File.format == 'txt'
        ).all()
        txts = { f.id: (join(self.index.path, f.path), f.label) for f in txts }
        return txts

    def get_channelset(self) -> List[str]:
        edfs = self.index.db.query(Metadata).group_by(Metadata.channels).all()
        edfs = [set(json.loads(edf.channels)) for edf in edfs]
        channels = edfs[0]
        for edf in edfs[1:]:
            channels = channels.intersection(edf)
        return sorted(channels)

    def get_lowest_frequency(self) -> float:
        frequency = self.index.db.query(func.min(Metadata.frequency)).all()
        if frequency is None:
            return 0
        return frequency[0][0]
