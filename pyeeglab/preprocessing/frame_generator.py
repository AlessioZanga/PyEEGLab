import logging
from typing import List

from math import floor
from json import dumps
from pandas import DataFrame

from .pipeline import Preprocessor


class DynamicWindow(Preprocessor):

    def __init__(self, frames: int) -> None:
        super().__init__()
        self.frames = frames
        logging.debug('Create dynamic frames (%d) generator preprocessor', frames)

    def to_json(self) -> str:
        json = {
            self.__class__.__name__ : {
                'frames': self.frames
            }
        }
        json = dumps(json)
        return json

    def run(self, data: DataFrame, **kwargs) -> List[DataFrame]:
        step = len(data)
        if self.frames > 1:
            step = floor(step/self.frames)
        return [data[t:t+step] for t in range(0, len(data) - step + 1, step)]
