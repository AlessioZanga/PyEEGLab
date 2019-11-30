import re
import json
import logging

from os import sched_getaffinity
from os.path import join, sep, isfile
from math import floor, ceil
from typing import List, Dict
from sqlalchemy import func
from multiprocessing import Pool
from ...database.index import File, Metadata
from ...io.loader import DataLoader
from ...io.raw import RawEDF
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):
    def __init__(self, path: str) -> None:
        logging.debug('Create TUH EEG Corpus Loader')
        if path[-1] != sep:
            path = path + sep
        self.index = TUHEEGArtifactIndex(path)

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        del state['index']
        return state

    def _parse_annotations(self, path: str, exclude: List[str] = ['null']) -> List:
        with open(path, 'r') as file:
            annotations = file.read()
        pattern = re.compile(r'^(\d+.\d+) (\d+.\d+) (\w+) (\d.\d+)$', re.MULTILINE)
        matches = re.findall(pattern, annotations)
        matches = [
            (float(m[0]), float(m[1]), m[2], float(m[3]))
            for m in matches if m[2] not in exclude
        ]
        return matches

    def _get_dataset(self, fid: str, path: str) -> List[RawEDF]:
        annotations = self._parse_annotations(path[:-4] + '.tse')
        edfs = []
        for annotation in annotations:
            edf = RawEDF(fid, path, annotation[2])
            tmax = ceil(annotation[1]-annotation[0])
            shift = floor(annotation[0])
            edf.set_tmax(tmax, shift)
            edfs.append(edf)
        return edfs

    def get_dataset(self) -> List[RawEDF]:
        files = self.index.db.query(File).filter(
            File.format == 'edf'
        ).all()
        files = [(f.id, join(self.index.path, f.path)) for f in files]
        pool = Pool(len(sched_getaffinity(0)))
        edfs = pool.starmap(self._get_dataset, files)
        pool.close()
        pool.join()
        edfs = [e for edf in edfs for e in edf]
        return edfs

    def get_dataset_text(self) -> Dict:
        txts = self.index.db.query(File).filter(
            File.format == 'txt'
        ).all()
        txts = { f.id: (join(self.index.path, f.path), f.label) for f in txts }
        return txts

    def get_channelset(self) -> List[str]:
        edfs = self.index.db.query(Metadata).group_by(Metadata.channels).all()
        edfs = [set(json.loads(edf.channels)) for edf in edfs]
        channels = edfs[0]
        for edf in edfs[1:]:
            channels = channels.intersection(edf)
        return sorted(channels)

    def get_lowest_frequency(self) -> float:
        frequency = self.index.db.query(func.min(Metadata.frequency)).all()
        if frequency is None:
            return 0
        return frequency[0][0]
