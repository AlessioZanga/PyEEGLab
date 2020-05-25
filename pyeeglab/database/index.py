import logging
from abc import ABC, abstractmethod
from typing import List

from os import walk
from uuid import uuid4
from json import dumps
from os.path import join, splitext
from multiprocessing import Pool
from mne import set_log_file
from multiprocessing import cpu_count

from sqlalchemy import Column, Integer, Float, Text, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

from ..io.raw import Raw


BaseTable = declarative_base()


class File(BaseTable):
    """File represents a single file contained in the dataset.
    
    This is an ORM class derived from the BaseTable in a declarative base
    used by SQLAlchemy.

    Attributes
    ----------
    id : str
        The primary key generated randomly using an UUID4 generator.
    channel_ref : str
        A not null indexed string describing the EEG channel reference system.
    extension : str
        A not null indexed string reporting the EEG recording format.
    path : str
        A not null string used to point to the relative path of the file respect
        to the current sqlite database location.
    """
    __tablename__ = 'file'
    id = Column(Text, primary_key=True)
    channel_ref = Column(Text, nullable=False, index=True)
    extension = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Metadata(BaseTable):
    """ Metadata represents a single metadata record associated with a single
    file contained in the dataset.

    This is an ORM class derived from the BaseTable in a declarative base
    used by SQLAlchemy.

    Attributes
    ----------
    file_id : str
        The foreign key related to file_id, used also as a primary key for metadata
        table since this is a one-to-one relationship.
    file_duration : int
        This is the EEG sample duration reported in seconds. This is not inteded as
        a precise duration estimate, but only a reference for statistical analysis.
        For more precise duration measurement, please, use the Raw record class methods.
    channels_count : int
        This field report the number of channels reported in the EEG header.
    ferquency : int
        The sample fequency expressend in Hz extrated from the EEG header.
    channels: str
        The list of channels saved as a JSON string extracted from the EEG header.
    """
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
    """Event represents a single event associated to a single file.
    Multiple events can be associated to multiple files, according to
    the record annotations.
    
    Attributes
    ----------
    id : str
        This is the primary key that is associated to each event. It is
        created from a UUID4.
    file_id : str
        This the foreign key that link the event to the related file.
    begin : float
        The timestep expressed in seconds from which the event begins.
    end : float
        The timestep expressed in seconds at which the event ends.
    duration : float
        The entire duration of the event.
    label : str
        The label of this event as written inthe annotations.
    """
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
    """ An abstract class representing the Index mechanism that is used to
    discover the dataset structure.
    
    It is the first component that must be implemented in order to provide
    full support to a specific dataset. If the dataset structure is regular,
    the only method that must be implemented id "_get_file(path)".    
    """
    def __init__(self, db: str, path: str, include_extensions: List[str] = ['edf'], exclude_events: List[str] = None) -> None:
        """
        Parameters
        ----------
        db : str
            The database connection handle expressed as string. This is usually
            configured by the Loader class as a sqlite handle, but in theory it
            could be used with any type of database connection.
        
        """
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
        pool = Pool(cpu_count())
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
        pool = Pool(cpu_count())
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
        pool = Pool(cpu_count())
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
