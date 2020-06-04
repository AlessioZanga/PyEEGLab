import logging

from dataclasses import dataclass

from sqlalchemy import Column, Integer, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from ..io.raw import Raw

BaseTable = declarative_base()


@dataclass
class File(BaseTable):
    """File represents a single file contained in the dataset.

    This is an ORM class derived from the BaseTable in a declarative base
    used by SQLAlchemy.

    Attributes
    ----------
    id : str
        The primary key generated randomly using an UUID4 generator.
    extension : str
        A not null indexed string reporting the EEG recording format.
    path : str
        A not null string used to point to the relative path of the file respect
        to the current sqlite database location.
    """
    __tablename__ = 'file'
    id: str = Column(Text, primary_key=True)
    extension: str = Column(Text, nullable=False, index=True)
    path: str = Column(Text, nullable=False)


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
    max_value: float
        The max value sampled in this record across all channels.
    min_value: float
        The min value sampled in this record across all channels.
    """
    __tablename__ = 'metadata'
    file_id = Column(Text, ForeignKey('file.id'), primary_key=True)
    file_duration = Column(Integer, nullable=False)
    channels_count = Column(Integer, nullable=False)
    frequency = Column(Integer, nullable=False, index=True)
    channels = Column(Text, nullable=False, index=True)
    max_value = Column(Float)
    min_value = Column(Float)

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
