import re
import uuid
import json
import logging

from typing import List, Dict
from os import walk
from os.path import join, sep, splitext
from mne import set_log_file
from ...io import RawEDF
from ...database.index import File, Metadata, Event, Index


class EEGMMIDBIndex(Index):
    def __init__(self, path: str) -> None:
        logging.debug('Create EEG Motor Movement/Imagery Index')
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
            'label': 'NA',
            'channel_ref': 'NA',
            'format': meta[-1].split('.')[-1],
            'path': path[l:],
        }
        return metadata

    def _get_edf_metadata(self, edf: RawEDF) -> Dict:
        metadata = Metadata({
            'id': edf.id,
            'file_duration': edf.open().n_times/edf.open().info['sfreq'],
            'channels_count': edf.open().info['nchan'],
            'frequency': edf.open().info['sfreq'],
            'channels': json.dumps(edf.open().info['ch_names']),
        })
        return metadata

    def _get_edf_events(self, edf: RawEDF) -> List:
        events = edf.get_events()
        for event in events:
            event['id'] = str(uuid.uuid4())
            event['file_id'] = edf.id
        events = [Event(event) for event in events]
        return events

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
                    edf = RawEDF(f.id, join(self.path, f.path), None)
                    metadata = self._get_edf_metadata(edf)
                    logging.debug('Add file %s edf metadata to index', f.id)
                    self.db.add(metadata)
                    events = self._get_edf_events(edf)
                    logging.debug('Add file %s edf events to index', f.id)
                    self.db.add_all(events)
        logging.debug('Index files completed')
        self.db.commit()
