import re
import uuid
import logging

from typing import List, Dict
from os.path import join, sep

from ...io import Raw
from ...database import File, Event, Index


class TUHEEGArtifactIndex(Index):

    def __init__(self, path: str, exclude_events: List[str] = ['elpp', 'bckg', 'null']) -> None:
        logging.debug('Create TUH EEG Corpus Index')
        super().__init__('sqlite:///' + join(path, 'index.db'), path, exclude_events)
        self.index()

    def _get_file(self, path: str) -> Dict:
        length = len(self.path)
        meta = path[length:].split(sep)
        file = {
            'id': str(uuid.uuid5(uuid.NAMESPACE_X500, path[length:])),
            'channel_ref': meta[0],
            'extension': meta[-1].split('.')[-1],
            'path': path[length:],
        }
        file = File(file)
        logging.debug('Add file %s raw to index', file.id)
        return file

    def _get_record_events(self, file: File) -> List[Event]:
        logging.debug('Add file %s raw events to index', file.id)
        raw = Raw(file.id, join(self.path, file.path))
        path = raw.path[:-4] + '.tse'
        with open(path, 'r') as file:
            annotations = file.read()
        pattern = re.compile(r'^(\d+.\d+) (\d+.\d+) (\w+) (\d.\d+)$', re.MULTILINE)
        events = re.findall(pattern, annotations)
        events = [
            (str(uuid.uuid4()), raw.id, float(e[0]), float(e[1]), e[2])
            for e in events if e[2] not in self.exclude_events
        ]
        keys = ['id', 'file_id', 'begin', 'end', 'label']
        events = [dict(zip(keys, event)) for event in events]
        events = [Event(event) for event in events]
        return events
