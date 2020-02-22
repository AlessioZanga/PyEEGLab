import logging
from abc import ABC
from typing import List, Dict

from os import sched_getaffinity
from json import loads, dumps
from os.path import isfile, join, sep
from hashlib import md5
from multiprocessing import Pool

from .raw import Raw
from ..database import File, Metadata, Event, Index


class DataLoader(ABC):

    index: Index

    def __init__(self, path: str, exclude_channel_ref: List[str] = None, exclude_frequency: List[int] = None,
                 exclude_files: List[str] = None, minimum_event_duration: float = -1) -> None:
        logging.debug('Create data loader')
        if path[-1] != sep:
            path = path + sep
        self.path = path
        self.exclude_channel_ref = exclude_channel_ref
        self.exclude_frequency = exclude_frequency
        self.exclude_files = exclude_files
        self.minimum_event_duration = minimum_event_duration

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        del state['index']
        return state

    def _get_data_by_event(self, f: File, e: Event) -> Raw:
        path_edf = join(self.path, f.path)
        path_fif = path_edf + '_' + e.id + '_raw.fif.gz'
        if not isfile(path_fif):
            edf = Raw(f.id, path_edf, e.label)
            edf.crop(e.begin, e.end-e.begin)
            edf.open().save(path_fif)
        fif = Raw(f.id, path_fif, e.label)
        return fif
    
    def set_minimum_event_duration(self, minimum_event_duration: float) -> 'DataLoader':
        self.minimum_event_duration = minimum_event_duration

    def get_dataset(self) -> List[Raw]:
        files = self.index.db.query(File, Metadata, Event)
        files = files.filter(File.id == Metadata.file_id)
        files = files.filter(File.id == Event.file_id)
        if self.index.include_extensions:
            files = files.filter(File.extension.in_(self.index.include_extensions))
        if self.exclude_channel_ref:
            files = files.filter(~File.channel_ref.in_(self.exclude_channel_ref))
        if self.exclude_frequency:
            files = files.filter(~Metadata.frequency.in_(self.exclude_frequency))
        if self.exclude_files:
            files = files.filter(~File.path.in_(self.exclude_files))
        if self.minimum_event_duration > 0:
            files = files.filter(Event.duration >= self.minimum_event_duration)
        files = files.all()
        files = [(file[0], file[2]) for file in files]
        pool = Pool(len(sched_getaffinity(0)))
        fifs = pool.starmap(self._get_data_by_event, files)
        pool.close()
        pool.join()
        return fifs

    def get_dataset_text(self) -> Dict:
        txts = self.index.db.query(File, Event)
        txts = txts.filter(File.id == Event.file_id)
        txts = txts.filter(File.extension == 'txt')
        txts = txts.all()
        txts = {f.id: (join(self.index.path, f.path), e.label) for f, e in txts}
        return txts

    def get_channelset(self) -> List[str]:
        files = self.index.db.query(File, Metadata)
        files = files.filter(File.id == Metadata.file_id)
        if self.exclude_channel_ref:
            files = files.filter(~File.channel_ref.in_(self.exclude_channel_ref))
        if self.exclude_frequency:
            files = files.filter(~Metadata.frequency.in_(self.exclude_frequency))
        if self.exclude_files:
            files = files.filter(~File.path.in_(self.exclude_files))
        if self.minimum_event_duration > 0:
            files = files.filter(Event.duration >= self.minimum_event_duration)
        files = files.group_by(Metadata.channels)
        files = files.all()
        files = [file[1] for file in files]
        files = [set(loads(file.channels)) for file in files]
        channels = files[0]
        for file in files[1:]:
            channels = channels.intersection(file)
        return sorted(channels)

    def get_lowest_frequency(self) -> float:
        frequency = self.index.db.query(Metadata)
        if self.exclude_frequency:
            frequency = frequency.filter(~Metadata.frequency.in_(self.exclude_frequency))
        frequency = frequency.all()
        frequency = min([f.frequency for f in frequency], default=0)
        return frequency

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        value = [self.path] + [self.minimum_event_duration]
        if self.exclude_channel_ref:
            value += self.exclude_channel_ref
        if self.exclude_frequency:
            value += self.exclude_frequency
        value = dumps(value).encode()
        value = md5(value).hexdigest()
        value = int(value, 16)
        return value
