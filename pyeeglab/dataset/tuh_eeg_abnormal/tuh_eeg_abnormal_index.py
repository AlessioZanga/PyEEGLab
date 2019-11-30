import uuid
import json
import logging
import warnings

from typing import List, Dict
from os import walk
from os.path import join, sep, splitext
from mne import set_log_file
from mne.io import read_raw_edf
from ...database.index import File, Metadata, Index


class TUHEEGAbnormalIndex(Index):
    def __init__(self, path: str) -> None:
        logging.debug('Create TUH EEG Corpus Index')
        super().__init__('sqlite:///' + join(path, 'index.db'), path)
        logging.debug('Redirect MNE logging interface to file')
        set_log_file(join(path, 'mne.log'), overwrite=False)
        logging.debug('Disable MNE runtime warnings')
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        self.index()

    def _get_files(self) -> List[str]:
        logging.debug('Get files from path')
        files = [
            join(dirpath, filename)
            for dirpath, _, filenames in walk(self.path)
            for filename in filenames
            if splitext(filename)[1] not in ['.db', '.log']
        ]
        return files
    def _get_file_metadata(self, path: str) -> Dict:
        l = len(self.path)
        meta = path[l:].split(sep)
        metadata = {
            'id': str(uuid.uuid5(uuid.NAMESPACE_X500, path[l:])),
            'type': meta[0],
            'label': meta[1],
            'channel_ref': meta[2],
            'patient_id': meta[4],
            'session_id': meta[5],
            'format': meta[-1].split('.')[-1],
            'path': path[l:],
        }
        return metadata

    def _get_edf_metadata(self, fid: str, path: str) -> Dict:
        with read_raw_edf(path) as r:
            metadata = Metadata({
                'id': fid,
                'file_duration': r.n_times/r.info['sfreq'],
                'channels_count': r.info['nchan'],
                'frequency': r.info['sfreq'],
                'channels': json.dumps(r.info['ch_names']),
            })
        return metadata

    def index(self) -> None:
        logging.debug('Index files')
        files = self._get_files()
        for file in files:
            f = File(self._get_file_metadata(file))
            stm = self.db.query(File).filter(File.id == f.id).all()
            if not stm:
                logging.debug('Add file %s at %s to index', f.id, f.path)
                self.db.add(f)
                if f.format == 'edf':
                    path = join(self.path, f.path)
                    metadata = self._get_edf_metadata(f.id, path)
                    logging.debug('Add file %s edf metada to index', f.id)
                    self.db.add(metadata)
        logging.debug('Index files completed')
        self.db.commit()
