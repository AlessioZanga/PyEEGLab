import os
import logging

from uuid import uuid4

from typing import List

from .utils import rsync

from ..dataset import Dataset
from ..file import File
from ..metadata import Metadata
from ..annotation import Annotation


class TUHEEGAbnormalDataset(Dataset):

    def __init__(
            self,
            path: str = "./data/tuh_eeg_abnormal/",
            version: str = "2.0.0",
            exclude_channels_set: List[str] = [
                "BURSTS",
                "ECG EKG-REF",
                "EMG-REF",
                "IBI",
                "PHOTIC-REF",
                "PULSE RATE",
                "STI 014",
                "SUPPR"
            ],
        ) -> None:
        super().__init__(
            path=path,
            name="Temple University Hospital EEG Abnormal Dataset",
            version="v"+version,
            exclude_channels_set=exclude_channels_set,
        )
    
    def download(self, user: str = None, password: str = None) -> None:
        rsync(self.path, user, password, "tuh_eeg_abnormal", self.version)

    def _get_metadata(self, file: File) -> Metadata:
        meta = file.path.split(os.path.sep)
        metadata = super()._get_metadata(file)
        metadata.channels_reference = meta[-5]
        return metadata
    
    def _get_annotation(self, file: File) -> List[Annotation]:
        logging.debug("Add file %s annotations to index", file.uuid)
        return [
            Annotation(
                uuid=str(uuid4()),
                file_uuid=file.uuid,
                begin=60,
                end=120,
                label=file.path.split(os.path.sep)[-6],
            )
        ]
