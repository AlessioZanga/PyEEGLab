import uuid
import logging

from os.path import join, sep

from ...io import Raw
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
            'id': str(uuid.uuid5(uuid.NAMESPACE_X500, path[length:])),
            'channel_ref': 'NA',
            'extension': meta[-1].split('.')[-1],
            'path': path[length:],
        }
        file = File(file)
        return file
