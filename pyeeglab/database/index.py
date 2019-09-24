import logging
from abc import ABC, abstractmethod

from sqlalchemy import Column, Integer, Text, ForeignKey
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base


BaseTable = declarative_base()


class File(BaseTable):
    __tablename__ = 'file'
    id = Column(Text, primary_key=True)
    type = Column(Text, nullable=False, index=True)
    label = Column(Text, nullable=False, index=True)
    patient_id = Column(Text, nullable=False)
    session_id = Column(Text, nullable=False)
    format = Column(Text, nullable=False, index=True)
    path = Column(Text, nullable=False)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Metadata(BaseTable):
    __tablename__ = 'metadata'
    id = Column(Text, ForeignKey('file.id'), primary_key=True)
    file_duration = Column(Integer, nullable=False)
    channels_count = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False, index=True)
    channels = Column(Text, nullable=False, index=True)

    def __init__(self, dictionary) -> None:
        for k, v in dictionary.items():
            setattr(self, k, v)


class Index(ABC):

    def __init__(self, db: str, path: str) -> None:
        logging.debug('Create index at %s', db)
        logging.debug('Load index at %s', db)
        engine = create_engine(db)
        BaseTable.metadata.create_all(engine)
        Session = sessionmaker(bind=engine)
        self.db = Session()
        self.path = path

    @abstractmethod
    def index(self) -> None:
        pass
