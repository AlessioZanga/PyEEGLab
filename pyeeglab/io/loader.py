import json
import logging
from abc import ABC
from typing import List, Dict

from os import sched_getaffinity
from os.path import isfile, join, sep
from multiprocessing import Pool

from sqlalchemy import func

from .raw import Raw
from ..database import File, Metadata, Event


class DataLoader(ABC):

    def __init__(self, path: str, extension: str = 'edf', exclude_channel_ref: List[str] = [], exclude_frequency: List[int] = []) -> None:
        logging.debug('Create data loader')
        if path[-1] != sep:
            path = path + sep
        self.path = path
        self.index = None
        self.extension = extension
        self.exclude_channel_ref = exclude_channel_ref
        self.exclude_frequency = exclude_frequency

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        del state['index']
        return state

    def _get_data_by_event(self, f: File, e: Event) -> Raw:
        path_edf = join(self.path, f.path)
        path_fif = path_edf + '-' + e.id + '.fif.gz'
        if not isfile(path_fif):
            edf = Raw(f.id, path_edf, e.label)
            edf.crop(e.begin, e.end-e.begin)
            edf.open().save(path_fif)
        fif = Raw(f.id, path_fif, e.label)
        return fif

    def get_dataset(self) -> List[Raw]:
        files = self.index.db.query(File, Metadata, Event)
        files = files.filter(File.id == Metadata.file_id)
        files = files.filter(File.id == Event.file_id)
        files = files.filter(File.format == self.extension)
        files = files.filter(~File.channel_ref.in_(self.exclude_channel_ref))
        files = files.filter(~Metadata.frequency.in_(self.exclude_frequency))
        files = files.all()
        files = [(file[0], file[2]) for file in files]
        pool = Pool(len(sched_getaffinity(0)))
        fifs = pool.starmap(self._get_data_by_event, files)
        pool.close()
        pool.join()
        return fifs

    def get_dataset_text(self) -> Dict:
        txts = self.index.db.query(File).filter(
            File.format == 'txt'
        ).all()
        txts = {f.id: (join(self.index.path, f.path), f.label) for f in txts}
        return txts

    def get_channelset(self) -> List[str]:
        files = self.index.db.query(File, Metadata)
        files = files.filter(File.id == Metadata.file_id)
        files = files.filter(~File.channel_ref.in_(self.exclude_channel_ref))
        files = files.filter(~Metadata.frequency.in_(self.exclude_frequency))
        files = files.group_by(Metadata.channels)
        files = files.all()
        files = [file[1] for file in files]
        files = [set(json.loads(file.channels)) for file in files]
        channels = files[0]
        for file in files[1:]:
            channels = channels.intersection(file)
        return sorted(channels)

    def get_lowest_frequency(self) -> float:
        frequency = self.index.db.query(Metadata)
        frequency = frequency.filter(~Metadata.frequency.in_(self.exclude_frequency))
        frequency = frequency.all()
        frequency = min([f.frequency for f in frequency], default=0)
        return frequency
