import os
import uuid
import json
import warnings
import mne

from ...database.index import File, Metadata, Index


class TUHEEGCorpusIndex(Index):
    def __init__(self, path):
        self._logger.debug('Create TUH EEG Corpus Index')
        super().__init__('sqlite:///' + os.path.join(path, 'index.db'), path)
        self._logger.debug('Redirect MNE logging interface to file')
        mne.set_log_file(os.path.join(path, 'mne.log'), overwrite=False)
        self._logger.debug('Disable MNE runtime warnings')
        warnings.filterwarnings("ignore", category=RuntimeWarning)
        self.index_files()

    def get_files_from_path(self, path):
        self._logger.debug('Get files from path')
        files = []
        for dirpath, _, filenames in os.walk(path):
            for file in filenames:
                if not file.endswith('.db') and not file.endswith('.log'):
                    files.append(os.path.join(dirpath, file))
        return files

    def get_metadata_from_file(self, path, file):
        meta = file[len(path):].split(os.path.sep)
        metadata = {
            'id': str(uuid.uuid5(uuid.NAMESPACE_X500, file[len(path):])),
            'type': meta[1],
            'label': meta[2],
            'patient_id': meta[5],
            'session_id': meta[6],
            'format': meta[-1].split('.')[-1],
            'path': file[len(path):],
        }
        return metadata

    def index_files(self):
        self._logger.debug('Index files')
        files = self.get_files_from_path(self.path())
        for file in files:
            f = File(self.get_metadata_from_file(self.path(), file))
            stm = self.db().query(File).filter(File.id == f.id).all()
            if not stm:
                self._logger.debug('Add file %s at %s to index', f.id, f.path)
                self.db().add(f)
                if f.format == 'edf':
                    path = os.path.join(self.path(), f.path)
                    with mne.io.read_raw_edf(path) as r:
                        m = Metadata({
                            'id': f.id,
                            'file_duration': r.n_times/r.info['sfreq'],
                            'channels_count': r.info['nchan'],
                            'frequency': r.info['sfreq'],
                            'channels': json.dumps(r.info['ch_names']),
                        })
                        self._logger.debug('Add file %s edf metada to index', f.id)
                        self.db().add(m)
        self._logger.debug('Index files completed')
        self.db().commit()
