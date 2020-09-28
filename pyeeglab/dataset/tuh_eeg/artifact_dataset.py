import os
import logging

from typing import List

from .utils import rsync, parse_tse

from ..dataset import Dataset
from ..file import File
from ..metadata import Metadata
from ..annotation import Annotation


class TUHEEGArtifactDataset(Dataset):

    def __init__(
            self,
            path: str = "./data/tuh_eeg_artifact/",
            version: str = "1.0.0",
            exclude_channels_set: List[str] = [
                "BURSTS",
                "EMG-REF",
                "IBI",
                "PHOTIC-REF",
                "SUPPR"
            ],
            exclude_channels_reference: List[str] = [
                "02_tcp_le",
                "03_tcp_ar_a"
            ],
        ) -> None:
        super().__init__(
            path=path,
            name="Temple University Hospital EEG Artifact Dataset",
            version="v"+version,
            exclude_channels_set=exclude_channels_set,
            exclude_channels_reference=exclude_channels_reference,
        )
    
    def download(self, user: str = None, password: str = None) -> None:
        rsync(self.path, user, password, "tuh_eeg_artifact", self.version)

    def _get_metadata(self, file: File) -> Metadata:
        meta = file.path.split(os.path.sep)
        metadata = super()._get_metadata(file)
        metadata.channels_reference = meta[-5]
        return metadata
    
    def _get_annotation(self, file: File) -> List[Annotation]:
        logging.debug("Add file %s annotations to index", file.uuid)
        return parse_tse(file)
