import json
import logging
from abc import ABC, abstractmethod
from typing import List, Dict
from os.path import join
from sqlalchemy import func
from ..database import File, Metadata

from .raw import Raw


class DataLoader(ABC):

    def __init__(self) -> None:
        logging.debug('Create data loader')
        self.index = None

    @abstractmethod
    def get_dataset(self) -> List[Raw]:
        pass

    def get_dataset_text(self) -> Dict:
        txts = self.index.db.query(File).filter(
            File.format == 'txt'
        ).all()
        txts = {f.id: (join(self.index.path, f.path), f.label) for f in txts}
        return txts

    def get_channelset(self, exclude_channel_ref: List[str] = []) -> List[str]:
        edfs = self.index.db.query(File, Metadata)
        edfs = edfs.filter(File.id == Metadata.id)
        edfs = edfs.filter(~File.channel_ref.in_(exclude_channel_ref))
        edfs = edfs.group_by(Metadata.channels).all()
        edfs = [edf[1] for edf in edfs]
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
