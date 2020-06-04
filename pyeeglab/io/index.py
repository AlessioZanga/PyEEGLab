import logging
import json

from abc import ABC, abstractmethod

from os import walk
from os.path import join, splitext
from uuid import uuid4
from multiprocessing import Pool, cpu_count
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from mne import set_log_file

from ..database import BASE_TABLE, File, Metadata, Event
from .raw import Raw

from typing import List


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
        BASE_TABLE.metadata.create_all(engine)
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
        return Metadata(
            file_id=raw.id,
            duration=raw.open().n_times/raw.open().info['sfreq'],
            channels_count=raw.open().info['nchan'],
            channels_set=json.dumps(raw.open().info['ch_names']),
            sampling_frequency=raw.open().info['sfreq'],
            max_value=raw.open().get_data().max(),
            min_value=raw.open().get_data().min(),
        )

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
        events = [Event(**event) for event in events]
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
            raws = [
                file for file in files if file.extension in self.include_extensions]
        metadata = self._parallel_record_metadata(raws)
        events = self._parallel_record_events(raws)
        self.db.add_all(files + metadata + events)
        self.db.commit()
        logging.debug('Index files completed')
