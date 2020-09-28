import os
import json
import logging
import hashlib
import pickle

from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import reduce
from multiprocessing import Pool, cpu_count
from operator import add, and_
from uuid import uuid4, uuid5, NAMESPACE_X500

from typing import Dict, List, Tuple

import mne
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker, Query

from .declarative_base import Base
from .file import File
from .metadata import Metadata
from .annotation import Annotation

from ..pipeline import Pipeline


@dataclass(init=False)
class Dataset(ABC):
    path: str
    name: str
    version: str

    extensions: List[str]
    exclude_file: List[str]
    exclude_channels_set: List[str]
    exclude_channels_reference: List[str]
    exclude_sampling_frequency: List[int]
    minimum_annotation_duration: float

    session: Session
    query: Query

    pipeline: Pipeline = None

    def __init__(
            self,
            path: str,
            name: str,
            version: str = None,
            extensions: List[str] = [".edf"],
            exclude_file: List[str] = None,
            exclude_channels_set: List[str] = None,
            exclude_channels_reference: List[str] = None,
            exclude_sampling_frequency: List[str] = None,
            minimum_annotation_duration: float = None
        ) -> None:
        # Set basic attributes
        self.path = os.path.abspath(os.path.join(path, version))
        self.name = name
        self.version = version

        # Set data set filter attributes
        self.extensions = extensions if extensions else []
        self.exclude_file = exclude_file if exclude_file else []
        self.exclude_channels_set = exclude_channels_set if exclude_channels_set else []
        self.exclude_channels_reference = exclude_channels_reference if exclude_channels_reference else []
        self.exclude_sampling_frequency = exclude_sampling_frequency if exclude_sampling_frequency else []
        self.minimum_annotation_duration = minimum_annotation_duration if minimum_annotation_duration else 0

        logging.info("Init dataset '%s'@'%s' at '%s'", self.name, self.version, self.path)

        # Make workspace directory
        logging.debug("Make .pyeeglab directory")
        workspace = os.path.join(self.path, ".pyeeglab")
        os.makedirs(workspace, exist_ok=True)
        logging.debug("Make .pyeeglab/cache directory")
        os.makedirs(os.path.join(workspace, "cache"), exist_ok=True)
        logging.debug("Set MNE log .pyeeglab/mne.log")
        mne.set_log_file(os.path.join(workspace, "mne.log"), overwrite=False)

        # Index data set files
        self.index()

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        for attribute in ["session", "query"]:
            if hasattr(self, attribute):
                del state[attribute]
        return state

    @abstractmethod
    def download(self, user: str = None, password: str = None) -> None:
        pass

    def index(self) -> None:
        # Init index session
        logging.debug("Make index session")
        connection = os.path.join(self.path, ".pyeeglab", "index.sqlite3")
        connection = create_engine("sqlite:///" + connection)
        Base.metadata.create_all(connection)
        self.session = sessionmaker(bind=connection)()
        # Open multiprocess pool
        logging.info("Index data set directory")
        pool = Pool(cpu_count())
        # Get files path from data set path
        paths = [
            os.path.join(directory, filename)
            for directory, _, filenames in os.walk(self.path)
            for filename in filenames
        ]
        # Get Files instances form paths, filtering already indexed
        files = self.session.query(File).all()
        files = [file.uuid for file in files]
        files = [
            file
            for file in pool.map(self._get_file, paths)
            if file.uuid not in files
        ]
        for file in files:
            logging.debug("Add file %s to index", file.uuid)
        # Filter raw data files by extension
        raws = [
            file
            for file in files
            if os.path.splitext(file.path)[-1] in self.extensions
        ]
        # Get metadata and annotation for data files
        metadatas = pool.map(self._get_metadata, raws)
        annotations = pool.map(self._get_annotation, raws)
        # Close multiprocess pool
        pool.close()
        pool.join()
        # Commit insertions to index
        commits = files + metadatas + reduce(add, annotations, [])
        if commits:
            logging.info("Commit insertions to index")
            self.session.add_all(commits)
            self.session.commit()
        logging.info("Index data set completed")
        # Init default query
        logging.debug("Init default query")
        self.query = self.session.query(File, Metadata, Annotation).\
            join(File.meta).\
            join(File.annotations).\
            filter(~Metadata.channels_reference.in_(self.exclude_channels_reference)).\
            filter(~Metadata.sampling_frequency.in_(self.exclude_sampling_frequency)).\
            filter((Annotation.end - Annotation.begin) >= self.minimum_annotation_duration)
        # Filter exclude file paths
        for file in self.exclude_file:
            self.query = self.query.filter(~File.path.like("%{}%".format(file)))
        logging.debug("SQL query representation: '%s'", str(self.query).replace("\n", ""))
    
    def _get_file(self, path: str) -> File:
        return File(
            uuid=str(uuid5(NAMESPACE_X500, path)),
            path=path,
            extension=os.path.splitext(path)[-1]
        )

    def _get_metadata(self, file: File) -> Metadata:
        logging.debug("Add file %s metadata to index", file.uuid)
        with file as reader:
            info = reader.info
            metadata = Metadata(
                file_uuid=file.uuid,
                duration=reader.n_times/info["sfreq"],
                channels_set=json.dumps(info["ch_names"]),
                sampling_frequency=info["sfreq"],
                max_value=reader.get_data().max(),
                min_value=reader.get_data().min(),
            )
        return metadata

    def _get_annotation(self, file: File) -> List[Annotation]:
        logging.debug("Add file %s annotations to index", file.uuid)
        with file as reader:
            annotations = [
                Annotation(
                    uuid=str(uuid4()),
                    file_uuid=file.uuid,
                    begin=annotation[0],
                    end=annotation[0]+annotation[1],
                    label=annotation[2],
                )
                for annotation in reader.annotations
            ]
        return annotations
    
    @property
    def environment(self) -> Dict:
        min_max = self.signal_min_max_range
        return {
            "channels_set": self.maximal_channels_subset,
            "lowest_frequency": self.lowest_frequency,
            "min_value": min_max[0],
            "max_value": min_max[1],
        }
    
    @property
    def lowest_frequency(self) -> float:
        frequency = self.query.all()
        frequency = min([
            f[1].sampling_frequency
            for f in frequency
        ], default=0)
        return frequency

    @property
    def maximal_channels_subset(self) -> List[str]:
        channels = self.query.group_by(Metadata.channels_set).all()
        channels = [
            frozenset(json.loads(channel[1].channels_set))
            for channel in channels
        ]
        channels = reduce(and_, channels)
        channels = channels - frozenset(self.exclude_channels_set)
        channels = sorted(channels)
        return channels
    
    @property
    def signal_min_max_range(self) -> Tuple[float]:
        min_max = self.query.all()
        min_max = [m[1] for m in min_max]
        min_max = tuple([
            min([m.min_value for m in min_max], default=0),
            max([m.max_value for m in min_max], default=0),
        ])
        return min_max
    
    def set_pipeline(self, pipeline: Pipeline) -> "Dataset":
        self.pipeline = pipeline
        self.pipeline.environment.update(self.environment)
        return self
    
    def set_minimum_event_duration(self, duration: float) -> "Dataset":
        logging.warning("This function will be deprecated in the near future")
        self.minimum_annotation_duration = duration
        return self
    
    def load(self) -> Dict:
        # Compute cache path
        cache = os.path.join(self.path, ".pyeeglab", "cache")
        # Compute cache key
        logging.info("Compute cache key")
        name = self.__class__.__name__.lower()
        if name.endswith("dataset"):
            name = name[:-len("dataset")]
        key = [hash(self), hash(self.pipeline)]
        key = [str(k).encode() for k in key]
        key = [hashlib.md5(k).hexdigest()[:10] for k in key]
        key = list(zip(["loader", "pipeline"], key))
        key = ["_".join(k) for k in key]
        key = name + "_" + "_".join(key)
        logging.info("Computed cache key: %s", key)
        # Load file cache
        cache = os.path.join(cache, key + ".pkl")
        if os.path.exists(cache):
            logging.info("Cache file found at %s", cache)
            with open(cache, "rb") as reader:
                try:
                    logging.info("Loading cache file")
                    return pickle.load(reader)
                except:
                    logging.error("Loading cache file failed")
        # Cache file not found, start preprocessing
        logging.info("Cache file not found, genereting new one")
        data = [row[2] for row in self.query.all()]
        data = self.pipeline.run(data)
        with open(cache, "wb") as file:
            logging.info("Dumping cache file")
            pickle.dump(data, file)
        return data
    
    def __hash__(self) -> int:
        key = [self.path, self.version, self.minimum_annotation_duration]
        key += self.exclude_file
        key += self.exclude_channels_set
        key += self.exclude_channels_reference
        key += self.exclude_sampling_frequency
        key = json.dumps(key).encode()
        key = hashlib.md5(key).hexdigest()
        key = int(key, 16)
        return key
