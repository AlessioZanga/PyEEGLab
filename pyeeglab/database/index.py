import uuid
import json
import logging
from abc import ABC, abstractmethod
from typing import List

from os import walk
from os.path import join, splitext
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
    label = Column(Text, nullable=False, index=True)
    channel_ref = Column(Text, nullable=False, index=True)
    format = Column(Text, nullable=False, index=True)
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
    label = Column(Text, nullable=False, index=True)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Index(ABC):

    def __init__(self, db: str, path: str, exclude_events: List[str] = []) -> None:
        logging.debug('Create index at %s', db)
        logging.debug('Load index at %s', db)
        engine = create_engine(db)
        BaseTable.metadata.create_all(engine)
        self.db = sessionmaker(bind=engine)()
        self.path = path
        self.exclude_events = exclude_events
        logging.debug('Redirect MNE logging interface to file')
        set_log_file(join(path, 'mne.log'), overwrite=False)

    @abstractmethod
    def index(self) -> None:
        pass

    def _get_files(self, exclude_extensions: List[str] = ['.db', '.gz', '.log']) -> List[str]:
        logging.debug('Get files from path')
        files = [
            join(dirpath, filename)
            for dirpath, _, filenames in walk(self.path)
            for filename in filenames
            if splitext(filename)[1] not in exclude_extensions
        ]
        return files

    @abstractmethod
    def _get_file(self, path: str) -> File:
        pass

    def _get_record_metadata(self, raw: Raw) -> Metadata:
        metadata = {
            'file_id': raw.id,
            'file_duration': raw.open().n_times/raw.open().info['sfreq'],
            'channels_count': raw.open().info['nchan'],
            'frequency': raw.open().info['sfreq'],
            'channels': json.dumps(raw.open().info['ch_names']),
        }
        metadata = Metadata(metadata)
        return metadata

    def _get_record_events(self, raw: Raw) -> List[Event]:
        events = raw.get_events()
        for event in events:
            event['id'] = str(uuid.uuid4())
            event['file_id'] = raw.id
        events = [Event(event) for event in events]
        return events
