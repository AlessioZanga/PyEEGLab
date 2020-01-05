import json
import logging

from os import sched_getaffinity
from os.path import join, sep
from math import floor, ceil
from typing import List, Dict
from multiprocessing import Pool
from sqlalchemy import func
from ...database.index import File, Metadata, Event
from ...io.loader import DataLoader
from ...io.raw import RawEDF
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):
    def __init__(self, path: str) -> None:
        super().__init__()
        logging.debug('Create TUH EEG Corpus Loader')
        if path[-1] != sep:
            path = path + sep
        self.path = path
        self.index = TUHEEGArtifactIndex(path)

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        del state['index']
        return state

    def _get_dataset(self, f: File, e: Event) -> RawEDF:
        edf = RawEDF(f.id, join(self.path, f.path), e.label)
        offset = floor(e.begin)
        length = ceil(e.end-e.begin)
        edf.crop(offset, length)
        return edf

    def get_dataset(self, exclude_channel_ref: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> List[RawEDF]:
        files = self.index.db.query(File, Event)
        files = files.filter(File.id == Event.file_id)
        files = files.filter(
            File.format == 'edf',
            ~File.channel_ref.in_(exclude_channel_ref)
        ).all()
        pool = Pool(len(sched_getaffinity(0)))
        edfs = pool.starmap(self._get_dataset, files)
        pool.close()
        pool.join()
        return edfs

    def get_dataset_text(self) -> Dict:
        txts = self.index.db.query(File).filter(
            File.format == 'txt'
        ).all()
        txts = {f.id: (join(self.index.path, f.path), f.label) for f in txts}
        return txts

    def get_channelset(self, exclude: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> List[str]:
        edfs = self.index.db.query(File, Metadata)
        edfs = edfs.filter(File.id == Metadata.id)
        edfs = edfs.filter(~File.channel_ref.in_(exclude))
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
