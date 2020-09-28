from dataclasses import dataclass
from mne.io import Raw, read_raw
from sqlalchemy import Column, ForeignKey, Text, Float
from sqlalchemy.orm import relationship
from .declarative_base import Base


@dataclass
class Annotation(Base):
    __tablename__ = "annotation"
    uuid: str = Column(Text, primary_key=True)
    file_uuid: str = Column(Text, ForeignKey("file.uuid"), nullable=False)
    begin: float = Column(Float, nullable=False)
    end: float = Column(Float, nullable=False)
    label: str = Column(Text, nullable=False, index=True)

    file = relationship("File", lazy="subquery")

    @property
    def duration(self) -> float:
        return self.end - self.begin
    
    def __enter__(self) -> Raw:
        self.reader = read_raw(self.file.path)
        tmax = self.reader.n_times / self.reader.info["sfreq"] - 0.1
        tmax = tmax if self.end > tmax else self.end
        self.reader.crop(self.begin, tmax)
        return self.reader

    def __exit__(self, *args, **kwargs) -> None:
        self.reader.close()
        del self.reader

