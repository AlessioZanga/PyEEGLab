import uuid
import logging

from os.path import join, sep
from ...io import RawEDF
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
            'label': 'NA',
            'channel_ref': 'NA',
            'format': meta[-1].split('.')[-1],
            'path': path[length:],
        }
        file = File(file)
        return file

    def index(self) -> None:
        logging.debug('Index files')
        files = self._get_files()
        for file in files:
            f = self._get_file(file)
            stm = self.db.query(File).filter(File.id == f.id).all()
            if not stm:
                logging.debug('Add file %s at %s to index', f.id, f.path)
                self.db.add(f)
                if f.format == 'edf':
                    edf = RawEDF(f.id, join(self.path, f.path), None)
                    metadata = self._get_record_metadata(edf)
                    logging.debug('Add file %s edf metadata to index', f.id)
                    self.db.add(metadata)
                    events = self._get_record_events(edf)
                    logging.debug('Add file %s edf events to index', f.id)
                    self.db.add_all(events)
        logging.debug('Index files completed')
        self.db.commit()
