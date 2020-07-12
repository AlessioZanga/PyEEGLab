import logging
import re
import json
import numpy as np

from typing import List

from uuid import uuid4, uuid5, NAMESPACE_X500
from os.path import join, sep

from ...io import Index, Raw
from ...database import File, Metadata, Event


class TUHEEGSeizureIndex(Index):

    def __init__(self, path: str, exclude_events: List = ['bckg', 'spsz']) -> None:
        logging.debug('Create TUH EEG Corpus Index')
        super().__init__('sqlite:///' + join(path, 'index.db'), path, exclude_events=exclude_events)
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
        metadata.channels_reference = meta[1]
        return metadata
    
    def _get_record_events(self, file: File) -> List[Event]:
        logging.debug('Add file %s raw events to index', file.id)
        raw = Raw(file.id, join(self.path, file.path))
        path = raw.path[:-4] + '.lbl'
        with open(path, 'r') as file:
            annotations = file.read()
        pattern = re.compile(
            r'^symbols\[0\] = ({.*})$',
            re.MULTILINE
        )
        mapper = re.findall(pattern, annotations)
        mapper = eval(mapper[0])
        events = re.findall(pattern, annotations)
        pattern = re.compile(
            r'^label = {([^,]*), ([^,]*), ([^,]*), ([^,]*), ([^,]*), ([^}]*)}$',
            re.MULTILINE
        )
        events = re.findall(pattern, annotations)
        labels = {}
        for event in events:
            intervall = (event[2], event[3])
            if intervall not in labels:
                labels[intervall] = {}
            channel = event[4]
            if channel not in labels[intervall]:
                labels[intervall][channel] = []
            label = np.array(json.loads(event[5]))
            for i in list(np.nonzero(label)[0]):
                labels[intervall][channel].append(mapper[i])
        labels = {
            (intervall[0], intervall[1], label)
            for intervall, channels in labels.items()
            for channel, labels in channels.items()
            for label in labels
        }
        events = [
            Event(
                id=str(uuid4()),
                file_id=raw.id,
                begin=float(label[0]),
                end=float(label[1]),
                duration=(float(label[1])-float(label[0])),
                label=label[2]
            )
            for label in labels
        ]
        return events
