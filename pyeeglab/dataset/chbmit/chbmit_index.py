import logging

from typing import List

from uuid import uuid4, uuid5, NAMESPACE_X500
from os.path import isfile, join, sep
from wfdb import rdann

from ...database import File, Event, Index


class CHBMITIndex(Index):
    def __init__(self, path: str) -> None:
        logging.debug('Create CHB-MIT Scalp EEG Index')
        super().__init__('sqlite:///' + join(path, 'index.db'), path)
        self.index()

    def _get_file(self, path: str) -> File:
        length = len(self.path)
        meta = path[length:].split(sep)
        file = {
            'id': str(uuid5(NAMESPACE_X500, path[length:])),
            'channel_ref': 'NA',
            'extension': meta[-1].split('.')[-1],
            'path': path[length:],
        }
        return File(file)

    def _get_record_events(self, file: File) -> List[Event]:
        logging.debug('Add file %s raw events to index', file.id)
        path = join(self.path, file.path)
        if isfile(path + '.seizures'):
            events = rdann(path, 'seizures')
            events = list(events.sample / events.fs)
            events = [events[i:i+2] for i in range(0, len(events), 2)]
            events = [
                Event({
                    'id': str(uuid4()),
                    'file_id': file.id,
                    'begin': event[0],
                    'end': event[1],
                    'duration': event[1] - event[0],
                    'label': 'seizure'
                })
                for event in events
            ]
        else:
            events = [
                Event({
                    'id': str(uuid4()),
                    'file_id': file.id,
                    'begin': 60,
                    'end': 120,
                    'duration': 60,
                    'label': 'noseizure'
                })
            ]
        return events
