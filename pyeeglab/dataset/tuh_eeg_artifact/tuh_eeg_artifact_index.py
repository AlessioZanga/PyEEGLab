import re
import uuid
import json
import logging

from typing import List, Dict
from os import walk
from os.path import join, sep, splitext
from mne import set_log_file
from mne.io import read_raw_edf
from ...database.index import File, Metadata, Event, Index


class TUHEEGArtifactIndex(Index):
    def __init__(self, path: str) -> None:
        logging.debug('Create TUH EEG Corpus Index')
        super().__init__('sqlite:///' + join(path, 'index.db'), path)
        logging.debug('Redirect MNE logging interface to file')
        set_log_file(join(path, 'mne.log'), overwrite=False)
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
            'type': 'NA',
            'label': 'NA',
            'channel_ref': meta[0],
            'patient_id': meta[2],
            'session_id': meta[3],
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

    def _get_edf_events(self, fid: str, path: str, exclude: List[str]) -> List:
        path = path[:-4] + '.tse'
        with open(path, 'r') as file:
            annotations = file.read()
        pattern = re.compile(r'^(\d+.\d+) (\d+.\d+) (\w+) (\d.\d+)$', re.MULTILINE)
        events = re.findall(pattern, annotations)
        events = [
            (str(uuid.uuid4()), fid, float(e[0]), float(e[1]), e[2])
            for e in events if e[2] not in exclude
        ]
        keys = ['id', 'file_id', 'begin', 'end', 'label']
        events = [dict(zip(keys, event)) for event in events]
        events = [Event(event) for event in events]
        return events

    def index(self, exclude_events: List[str] = ['elpp', 'bckg', 'null']) -> None:
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
                    logging.debug('Add file %s edf metadata to index', f.id)
                    self.db.add(metadata)
                    events = self._get_edf_events(f.id, path, exclude_events)
                    logging.debug('Add file %s edf events to index', f.id)
                    self.db.add_all(events)
        logging.debug('Index files completed')
        self.db.commit()
