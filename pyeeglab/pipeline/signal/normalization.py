import logging

from dataclasses import dataclass

from typing import List

import numpy as np
import pandas as pd

from ..preprocessor import Preprocessor


@dataclass
class AmplitudeNormalizer(Preprocessor):

    def __call__(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return data / data.abs().max()


@dataclass
class MinMaxNormalizer(Preprocessor):

    def __call__(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        return (data - data.min()) / (data.max() - data.min())


@dataclass
class MinMaxCenteredNormalizer(Preprocessor):

    def __call__(self, data: pd.DataFrame, **kwargs) -> pd.DataFrame:
        mean = (data.max() + data.min()) / 2
        return (data - mean) / mean
