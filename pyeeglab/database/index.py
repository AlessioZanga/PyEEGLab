import logging
from abc import ABC, abstractmethod
from typing import List

from os import walk, sched_getaffinity
from uuid import uuid4
from json import dumps
from os.path import join, splitext
from multiprocessing import Pool
from mne import set_log_file

from sqlalchemy import Column, Integer, Float, Text, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ..io.raw import Raw


BaseTable = declarative_base()


class File(BaseTable):
    __tablename__ = 'file'
    id = Column(Text, primary_key=True)
    channel_ref = Column(Text, nullable=False, index=True)
    extension = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Metadata(BaseTable):
    __tablename__ = 'metadata'
    file_id = Column(Text, ForeignKey('file.id'), primary_key=True)
    file_duration = Column(Integer, nullable=False)
    channels_count = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False, index=True)
    channels = Column(Text, nullable=False, index=True)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Event(BaseTable):
    __tablename__ = 'event'
    id = Column(Text, primary_key=True)
    file_id = Column(Text, ForeignKey('file.id'), index=True)
    begin = Column(Float, nullable=False)
    end = Column(Float, nullable=False)
    duration = Column(Float, nullable=False)
    label = Column(Text, nullable=False, index=True)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Index(ABC):

    def __init__(self, db: str, path: str, include_extensions: List[str] = ['edf'], exclude_events: List[str] = None) -> None:
        logging.debug('Create index at %s', db)
        logging.debug('Load index at %s', db)
        engine = create_engine(db)
        BaseTable.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.path = path
        self.include_extensions = include_extensions
        self.exclude_events = exclude_events
        logging.debug('Redirect MNE logging interface to file')
        set_log_file(join(path, 'mne.log'), overwrite=False)

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        del state['db']
        return state

    def _get_paths(self, exclude_extensions: List[str] = ['.db', '.gz', '.log']) -> List[str]:
        logging.debug('Get files from path')
        paths = [
            join(dirpath, filename)
            for dirpath, _, filenames in walk(self.path)
            for filename in filenames
            if splitext(filename)[1] not in exclude_extensions
        ]
        return paths

    @abstractmethod
    def _get_file(self, path: str) -> File:
        pass

    def _get_files(self, paths: List[str]) -> List[File]:
        pool = Pool(len(sched_getaffinity(0)))
        files = pool.map(self._get_file, paths)
        pool.close()
        pool.join()
        return files

    def _get_record_metadata(self, file: File) -> Metadata:
        logging.debug('Add file %s raw metadata to index', file.id)
        raw = Raw(file.id, join(self.path, file.path))
        metadata = {
            'file_id': raw.id,
            'file_duration': raw.open().n_times/raw.open().info['sfreq'],
            'channels_count': raw.open().info['nchan'],
            'frequency': raw.open().info['sfreq'],
            'channels': dumps(raw.open().info['ch_names']),
        }
        metadata = Metadata(metadata)
        return metadata

    def _parallel_record_metadata(self, files: List[File]) -> List[Metadata]:
        pool = Pool(len(sched_getaffinity(0)))
        metadata = pool.map(self._get_record_metadata, files)
        pool.close()
        pool.join()
        return metadata

    def _get_record_events(self, file: File) -> List[Event]:
        logging.debug('Add file %s raw events to index', file.id)
        raw = Raw(file.id, join(self.path, file.path))
        events = raw.get_events()
        for event in events:
            event['id'] = str(uuid4())
            event['file_id'] = raw.id
        events = [Event(event) for event in events]
        return events

    def _parallel_record_events(self, files: List[File]) -> List[Event]:
        pool = Pool(len(sched_getaffinity(0)))
        events = pool.map(self._get_record_events, files)
        pool.close()
        pool.join()
        events = [e for event in events for e in event]
        return events

    def index(self) -> None:
        logging.debug('Index files')
        files = self._get_paths()
        files = self._get_files(files)
        files = [
            file
            for file in files
            if not self.db.query(File).filter(File.id == file.id).all()
        ]
        for file in files:
            logging.debug('Add file %s raw to index', file.id)
        if self.include_extensions:
            raws = [file for file in files if file.extension in self.include_extensions]
        metadata = self._parallel_record_metadata(raws)
        events = self._parallel_record_events(raws)
        self.db.add_all(files + metadata + events)
        self.db.commit()
        logging.debug('Index files completed')
