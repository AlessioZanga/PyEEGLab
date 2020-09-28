from dataclasses import dataclass
from mne.io import Raw, read_raw
from sqlalchemy import Column, Text
from sqlalchemy.orm import relationship
from .declarative_base import Base


@dataclass
class File(Base):
    __tablename__ = "file"
    uuid: str = Column(Text, primary_key=True)
    path: str = Column(Text, nullable=False)
    extension: str = Column(Text, nullable=False)

    meta = relationship("Metadata", cascade="all,delete", backref="File")
    annotations = relationship("Annotation", cascade="all,delete", backref="File")

    def __enter__(self) -> Raw:
        self.reader = read_raw(self.path)
        return self.reader

    def __exit__(self, *args, **kwargs) -> None:
        self.reader.close()
        del self.reader
