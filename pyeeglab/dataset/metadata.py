from dataclasses import dataclass
from sqlalchemy import Column, ForeignKey, Text, Float, Integer
from .declarative_base import Base


@dataclass
class Metadata(Base):
    __tablename__ = "metadata"
    file_uuid: str = Column(Text, ForeignKey("file.uuid"), primary_key=True)
    duration: int = Column(Float, nullable=False)
    channels_set: str = Column(Text, nullable=False, index=True)
    channels_reference: str = Column(Text, nullable=True, index=True)
    sampling_frequency: int = Column(Integer, nullable=False, index=True)
    max_value: float = Column(Float, nullable=False)
    min_value: float = Column(Float, nullable=False)
