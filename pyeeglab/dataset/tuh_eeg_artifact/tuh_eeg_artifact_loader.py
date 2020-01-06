import logging

from os import sched_getaffinity
from os.path import isfile, join, sep
from typing import List
from multiprocessing import Pool
from ...database import File, Event
from ...io import DataLoader, RawEDF, RawFIF
from .tuh_eeg_artifact_index import TUHEEGArtifactIndex


class TUHEEGArtifactLoader(DataLoader):
    def __init__(self, path: str) -> None:
        super().__init__()
        logging.debug('Create TUH EEG Corpus Loader')
        if path[-1] != sep:
            path = path + sep
        self.path = path
        self.index = TUHEEGArtifactIndex(path)

    def __getstate__(self):
        # Workaround for unpickable sqlalchemy.orm.session
        # during multiprocess dataset loading
        state = self.__dict__.copy()
        del state['index']
        return state

    def _get_dataset_by_event(self, f: File, e: Event) -> RawEDF:
        path_edf = join(self.path, f.path)
        path_fif = path_edf + '-' + e.id + '.fif.gz'
        if not isfile(path_fif):
            edf = RawEDF(f.id, path_edf, e.label)
            edf.crop(e.begin, e.end-e.begin)
            edf.open().save(path_fif)
        fif = RawFIF(f.id, path_fif, e.label)
        return fif

    def get_dataset(self, exclude_channel_ref: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> List[RawEDF]:
        files = self.index.db.query(File, Event)
        files = files.filter(File.id == Event.file_id)
        files = files.filter(
            File.format == 'edf',
            ~File.channel_ref.in_(exclude_channel_ref)
        ).all()
        pool = Pool(len(sched_getaffinity(0)))
        fifs = pool.starmap(self._get_dataset_by_event, files)
        pool.close()
        pool.join()
        return fifs

    def get_channelset(self, exclude_channel_ref: List[str] = ['02_tcp_le', '03_tcp_ar_a']) -> List[str]:
        return super().get_channelset(exclude_channel_ref)
