import logging

from dataclasses import dataclass

from sqlalchemy import Column, Integer, Float, Text, ForeignKey
from sqlalchemy.ext.declarative import declarative_base

from ..io.raw import Raw


BASE_TABLE = declarative_base()


@dataclass
class File(BASE_TABLE):
    """File represents a single file contained in the dataset.

    This is an ORM class derived from the BASE_TABLE in a declarative base
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


@dataclass
class Metadata(BASE_TABLE):
    """ Metadata represents a single metadata record associated with a single
    file contained in the dataset.

    This is an ORM class derived from the BASE_TABLE in a declarative base
    used by SQLAlchemy.

    Attributes
    ----------
    file_id : str
        The foreign key related to file_id, used also as a primary key for metadata
        table since this is a one-to-one relationship.
    duration : int
        This is the EEG sample duration reported in seconds. This is not inteded as
        a precise duration estimate, but only a reference for statistical analysis.
        For more precise duration measurement, please, use the Raw record class methods.
    channels_count : int
        This field report the number of channels reported in the EEG header.
    channels_reference : str
        An indexed string describing the EEG channel reference system.
    channels_set : str
        The list of channels saved as a JSON string extracted from the EEG header.
    sampling_frequency : int
        The sampling fequency expressend in Hz extrated from the EEG header.
    max_value : float
        The max value sampled in this record across all channels.
    min_value : float
        The min value sampled in this record across all channels.
    """
    __tablename__ = 'metadata'
    file_id: str = Column(Text, ForeignKey('file.id'), primary_key=True)
    duration: int = Column(Integer, nullable=False)
    channels_count: int = Column(Integer, nullable=False)
    channels_reference: str = Column(Text, nullable=True, index=True)
    channels_set: str = Column(Text, nullable=False, index=True)
    sampling_frequency: int = Column(Integer, nullable=False, index=True)
    max_value: float = Column(Float, nullable=False)
    min_value: float = Column(Float, nullable=False)


@dataclass
class Event(BASE_TABLE):
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
    id: str = Column(Text, primary_key=True)
    file_id: str = Column(Text, ForeignKey('file.id'), index=True)
    begin: float = Column(Float, nullable=False)
    end: float = Column(Float, nullable=False)
    duration: float = Column(Float, nullable=False)
    label: str = Column(Text, nullable=False, index=True)
