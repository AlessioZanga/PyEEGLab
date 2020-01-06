import logging
import warnings

from importlib.util import find_spec
from mne.utils import set_config

from .dataset import TUHEEGAbnormalDataset, TUHEEGAbnormalLoader, TUHEEGArtifactDataset, TUHEEGArtifactLoader, EEGMMIDBDataset, EEGMMIDBLoader
from .io import Raw
from .preprocessing import GraphGenerator, Preprocessor
from .text import TextMiner

logging.getLogger().setLevel(logging.DEBUG)

if find_spec('cupy') is not None:
    set_config('MNE_USE_CUDA', 'true')

warnings.filterwarnings("ignore", category=RuntimeWarning)
