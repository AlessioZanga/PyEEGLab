import logging
import json

from typing import List

from uuid import uuid4, uuid5, NAMESPACE_X500
from os.path import join, sep

from ...io import Index, Raw
from ...database import File, Metadata, Event


class TUHEEGAbnormalIndex(Index):
    def __init__(self, path: str) -> None:
        logging.debug('Create TUH EEG Corpus Index')
        super().__init__('sqlite:///' + join(path, 'index.db'), path)
        self.index()

    def _get_file(self, path: str) -> File:
        length = len(self.path)
        meta = path[length:].split(sep)
        return File(
            id=str(uuid5(NAMESPACE_X500, path[length:])),
            extension=meta[-1].split('.')[-1],
            path=path[length:]
        )

    def _get_record_metadata(self, file: File) -> Metadata:
        meta = file.path.split(sep)
        metadata = super()._get_record_metadata(file)
        metadata.channels_reference = meta[2]
        return metadata

    def _get_record_events(self, file: File) -> List[Event]:
        logging.debug('Add file %s raw events to index', file.id)
        raw = Raw(file.id, join(self.path, file.path))
        return [
            Event(
                id=str(uuid4()),
                file_id=raw.id,
                begin=60,
                end=120,
                duration=60,
                label=raw.path.split(sep)[-6]
            )
        ]
