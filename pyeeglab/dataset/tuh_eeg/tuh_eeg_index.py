import uuid
import json
import logging
import warnings

from typing import List, Dict
from os import walk
from os.path import join, sep
from mne import set_log_file
from mne.io import read_raw_edf
from ...database.index import File, Metadata, Index


class TUHEEGCorpusIndex(Index):
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
        files = []
        for dirpath, _, filenames in walk(self.path):
            for file in filenames:
                if not file.endswith('.db') and not file.endswith('.log'):
                    files.append(join(dirpath, file))
        return files

    def _get_metadata_from_file(self, file: str) -> Dict:
        l = len(self.path)
        meta = file[l:].split(sep)
        metadata = {
            'id': str(uuid.uuid5(uuid.NAMESPACE_X500, file[l:])),
            'type': meta[1],
            'label': meta[2],
            'patient_id': meta[5],
            'session_id': meta[6],
            'format': meta[-1].split('.')[-1],
            'path': file[l:],
        }
        return metadata

    def index(self) -> None:
        logging.debug('Index files')
        files = self._get_files()
        for file in files:
            f = File(self._get_metadata_from_file(file))
            stm = self.db.query(File).filter(File.id == f.id).all()
            if not stm:
                logging.debug('Add file %s at %s to index', f.id, f.path)
                self.db.add(f)
                if f.format == 'edf':
                    path = join(self.path, f.path)
                    with read_raw_edf(path) as r:
                        m = Metadata({
                            'id': f.id,
                            'file_duration': r.n_times/r.info['sfreq'],
                            'channels_count': r.info['nchan'],
                            'frequency': r.info['sfreq'],
                            'channels': json.dumps(r.info['ch_names']),
                        })
                        logging.debug('Add file %s edf metada to index', f.id)
                        self.db.add(m)
        logging.debug('Index files completed')
        self.db.commit()
