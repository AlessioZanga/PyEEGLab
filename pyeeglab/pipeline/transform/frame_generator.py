from dataclasses import dataclass
from math import floor

from typing import List

import pandas as pd

from ..preprocessor import Preprocessor


@dataclass
class StaticWindow(Preprocessor):

    frames: int
    length: float

    def __call__(self, data: pd.DataFrame, **kwargs) -> List[pd.DataFrame]:
        step = floor(self.length * kwargs['lowest_frequency'])
        if (step * self.frames > len(data)):
            raise RuntimeError('Error while creating static frames: not enough data.')
        return [data[t:t+step] for t in range(0, step * self.frames, step)]


@dataclass
class StaticWindowOverlap(Preprocessor):

    frames: int
    length: float
    overlap: float

    def __call__(self, data: pd.DataFrame, **kwargs) -> List[pd.DataFrame]:
        step = floor(self.length * kwargs['lowest_frequency'])
        if (step * self.frames * (1 - self.overlap) > len(data)):
            raise RuntimeError('Error while creating static frames: not enough data.')
        return [data[t:t+step] for t in range(0, floor(step * self.frames * (1 - self.overlap)), floor(step * (1 - self.overlap)))]


@dataclass
class DynamicWindow(Preprocessor):

    frames: int

    def __call__(self, data: pd.DataFrame, **kwargs) -> List[pd.DataFrame]:
        step = len(data)
        if self.frames > 1:
            step = floor(step/self.frames)
        return [data[t:t+step] for t in range(0, len(data) - step + 1, step)]


@dataclass
class DynamicWindowOverlap(Preprocessor):

    frames: int
    overlap: float

    def __call__(self, data: pd.DataFrame, **kwargs) -> List[pd.DataFrame]:
        step = len(data)
        if self.frames > 1:
            step = floor(step/self.frames)
        return [data[t:t+step] for t in range(0, len(data) - step + 1, floor(step * (1 - self.overlap)))]
