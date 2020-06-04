import logging
import warnings

from importlib.util import find_spec
from mne.utils import set_config

from .dataset import TUHEEGAbnormalDataset, TUHEEGAbnormalLoader, \
    TUHEEGArtifactDataset, TUHEEGArtifactLoader, \
    EEGMMIDBDataset, EEGMMIDBLoader, \
    CHBMITLoader, CHBMITDataset
from .io import Raw
from .cache import PickleCache
from .pipeline import Pipeline, ForkedPreprocessor
from .preprocess import CommonChannelSet, LowestFrequency, BandPassFrequency, NotchFrequency, \
    ToDataframe, ToNumpy, ToNumpy1D, StaticWindow, DynamicWindow, \
    StaticWindowOverlap, DynamicWindowOverlap, SpearmanCorrelation, \
    BinarizedSpearmanCorrelation, CorrelationToAdjacency, \
    Bandpower, GraphGenerator, GraphWithFeatures, \
    ToMergedDataframes, Mean, Variance, Skewness, Kurtosis, ZeroCrossing, \
    AbsoluteArea, PeakToPeak, MinMaxNormalization, MinMaxCentralizedNormalization

logging.getLogger().setLevel(logging.DEBUG)

warnings.filterwarnings("ignore", category=RuntimeWarning)
