import json
import logging

import hashlib

from abc import ABC, abstractmethod
from dataclasses import dataclass

from typing import Any


class Preprocessor(ABC):

    def __init__(self) -> None:
        logging.debug("Init %s", self)

    @abstractmethod
    def __call__(self, data: Any, **kwargs):
        pass


@dataclass
class ForkedPreprocessor(Preprocessor):

    inputs: Any
    output: Any

    def __call__(self, data: Any, **kwargs):
        out = []
        for item in self.inputs:
            if isinstance(item, list):
                i = data
                for preprocessor in item:
                    i = preprocessor(i, **kwargs)
            if isinstance(item, Preprocessor):
                i = item(data, **kwargs)
            out.append(i)
        return self.output(out, **kwargs)
