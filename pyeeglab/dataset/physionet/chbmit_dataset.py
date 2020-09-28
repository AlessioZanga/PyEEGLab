import os
import logging

from uuid import uuid4

from typing import List

from .utils import wget

from ..dataset import Dataset
from ..file import File
from ..annotation import Annotation

import wfdb


class PhysioNetCHBMITDataset(Dataset):

    def __init__(
            self,
            path: str = "./data/physionet.org/files/chbmit/",
            version: str = "1.0.0",
            exclude_file: List[str] = [
                "chb03/chb03_35.edf",   # Corrupted data
                "chb12/chb12_27.edf",   # Bad channel names
                "chb12/chb12_28.edf",   # Bad channel names
                "chb12/chb12_29.edf",   # Bad channel names
            ],
            exclude_channels_set: List[str] = [
                "ECG",
                "LOC-ROC",
                "LUE-RAE",
                "VNS",
            ],
        ) -> None:
        super().__init__(
            path=path,
            name="CHB-MIT Scalp EEG Database",
            version=version,
            exclude_file=exclude_file,
            exclude_channels_set=exclude_channels_set,
        )
    
    def download(self, user: str = None, password: str = None) -> None:
        wget(self.path, user, password, "chbmit", self.version)
    
    def _get_annotation(self, file: File) -> List[Annotation]:
        logging.debug("Add file %s annotations to index", file.uuid)
        annotations = [
            Annotation(
                uuid=str(uuid4()),
                file_uuid=file.uuid,
                begin=60,
                end=120,
                label="noseizure"
            )
        ]
        if os.path.isfile(file.path + ".seizures"):
            annotations = wfdb.rdann(file.path, "seizures")
            annotations = list(annotations.sample / annotations.fs)
            annotations = [annotations[i:i+2] for i in range(0, len(annotations), 2)]
            annotations = [
                Annotation(
                    uuid=str(uuid4()),
                    file_uuid=file.uuid,
                    begin=annotation[0],
                    end=annotation[1],
                    label="seizure"
                )
                for annotation in annotations
            ]
        return annotations
