import os
import json
from sqlalchemy import func

from ...database.index import File, Metadata
from ...io.loader import DataLoader
from ...io.raw import RawEDF
from .tuh_eeg_index import TUHEEGCorpusIndex


class TUHEEGCorpusLoader(DataLoader):
    def __init__(self, path):
        self._logger.debug('Create TUH EEG Corpus Loader')
        if path[-1] != os.path.sep:
            path = path + os.path.sep
        self._index = TUHEEGCorpusIndex(path)

    def get_dataset(self):
        edfs = self.index().db().query(File).filter(
            File.format == 'edf'
        ).all()
        edfs = [
            RawEDF(f.id, os.path.join(self.index().path(), f.path), f.label)
            for f in edfs
        ]
        return edfs

    def get_dataset_text(self):
        txts = self.index().db().query(File).filter(
            File.format == 'txt'
        ).all()
        txts = {
            f.id: (os.path.join(self.index().path(), f.path), f.label)
            for f in txts
        }
        return txts

    def get_channelset(self):
        edf_metas = self.index().db().query(Metadata).group_by(Metadata.channels).all()
        edf_metas = [
            set(json.loads(edf_meta.channels))
            for edf_meta in edf_metas
        ]
        channels_set = edf_metas[0]
        for edf_meta in edf_metas[1:]:
            channels_set = channels_set.intersection(edf_meta)
        channels_set = list(channels_set)
        return channels_set

    def get_lowest_frequency(self):
        edf_metas = self.index().db().query(func.min(Metadata.frequency)).all()
        if edf_metas is None:
            return 0
        return edf_metas[0][0]
