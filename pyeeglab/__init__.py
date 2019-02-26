import logging

from .dataset import TUHEEGCorpusLoader
from .database import File, EDFMeta
from .io import EDFLoader
from .preprocessing import DataNormalizer

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(message)s'
)
