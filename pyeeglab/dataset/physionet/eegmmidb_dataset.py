import os
import logging

from uuid import uuid4

from typing import List

from .utils import wget

from ..dataset import Dataset
from ..file import File
from ..annotation import Annotation


class PhysioNetEEGMMIDBDataset(Dataset):

    def __init__(
            self,
            path: str = "./data/physionet.org/files/eegmmidb/",
            version: str = "1.0.0",
            exclude_file: List[str] = [
                "S021/S021R08.edf",     # Corrupted data
                "S104/S104R04.edf",     # Corrupted data
            ],
            exclude_sampling_frequency: List[int] = [ 128 ],
        ) -> None:
        super().__init__(
            path=path,
            name="EEG Motor Movement/Imagery Dataset",
            version=version,
            exclude_file=exclude_file,
            exclude_sampling_frequency=exclude_sampling_frequency,
        )
    
    def download(self, user: str = None, password: str = None) -> None:
        wget(self.path, user, password, "eegmmidb", self.version)
    
    def _get_annotation(self, file: File) -> List[Annotation]:
        logging.debug("Add file %s annotations to index", file.uuid)
        with file as reader:
            try:
                annotations = [
                    Annotation(
                        uuid=str(uuid4()),
                        file_uuid=file.uuid,
                        begin=annotation[0],
                        end=annotation[0]+annotation[1],
                        label=annotation[2],
                    )
                    for annotation in reader.annotations
                ]
            except KeyError:
                # Alternative annotation format
                annotations = [
                    Annotation(
                        uuid=str(uuid4()),
                        file_uuid=file.uuid,
                        begin=annotation["onset"],
                        end=annotation["onset"]+annotation["duration"],
                        label=annotation["description"],
                    )
                    for annotation in reader.annotations
                ]
        return annotations
