import logging

from uuid import uuid5, NAMESPACE_X500
from os.path import join, sep

from ...database import File, Index


class EEGMMIDBIndex(Index):
    def __init__(self, path: str) -> None:
        logging.debug('Create EEG Motor Movement/Imagery Index')
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
