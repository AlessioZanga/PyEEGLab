import logging
from abc import ABC, abstractmethod

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base


BaseTable = declarative_base()


class File(BaseTable):
    __tablename__ = 'file'
    id = Column(Text, primary_key=True)
    type = Column(Text, nullable=False, index=True)
    eeg_class = Column(Text, nullable=False, index=True)
    patient_id = Column(Text, nullable=False)
    session_id = Column(Text, nullable=False)
    format = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False)

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class EDFMeta(BaseTable):
    __tablename__ = 'edf_metadata'
    id = Column(Text, ForeignKey('file.id'), primary_key=True)
    file_duration = Column(Integer, nullable=False)
    signal_count = Column(Integer, nullable=False)
    sample_frequency = Column(Integer, nullable=False, index=True)
    channels = Column(Text, nullable=False, index=True)

    def __init__(self, dictionary):
        for k, v in dictionary.items():
            setattr(self, k, v)


class Index(ABC):
    _db = None
    _path = None
    _logger = logging.getLogger()

    def __init__(self, path):
        self._path = path
        self._logger.debug('Create index at %s', self._path)

    @abstractmethod
    def loadIndex(self):
        pass

    @abstractmethod
    def indexFiles(self):
        pass

    def db(self):
        return self._db

    def path(self):
        return self._path
