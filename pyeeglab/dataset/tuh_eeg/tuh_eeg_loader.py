from ...database.index import File, EDFMeta
from ...io.loader import DataLoader, EDFLoader
from .tuh_eeg_index import TUHEEGCorpusIndex

import os
import json


class TUHEEGCorpusLoader(DataLoader):
    def __init__(self, path):
        if path[-1] != os.path.sep:
            path = path + os.path.sep
        self._index = TUHEEGCorpusIndex(path)

    def getTrainSet(self):
        raise NotImplementedError

    def getTestSet(self):
        raise NotImplementedError

    def getEDFSet(self):
        edfs = self.index().db().query(File).filter(
            File.format == 'edf'
        ).all()
        edfs = [
            EDFLoader(file.id, os.path.join(self.index().path(), file.path))
            for file in edfs
        ]
        return edfs

    def getEDFSetByFrequency(self, frequency=250):
        edfs = self.index().db().query(File).filter(
            File.format == 'edf'
        ).filter(
            EDFMeta.id == File.id
        ).filter(
            EDFMeta.sample_frequency == frequency
        ).all()
        edfs = [
            EDFLoader(file.id, os.path.join(self.index().path(), file.path))
            for file in edfs
        ]
        return edfs

    def getChannelSet(self):
        edf_metas = self.index().db().query(EDFMeta).group_by(EDFMeta.channels).all()
        edf_metas = [
            set(json.loads(edf_meta.channels))
            for edf_meta in edf_metas
        ]
        channels_set = edf_metas[0]
        for edf_meta in edf_metas[1:]:
            channels_set = channels_set.intersection(edf_meta)
        channels_set = list(channels_set)
        return channels_set
