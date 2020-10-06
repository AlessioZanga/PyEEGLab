import logging
import warnings

logging.basicConfig(
    format="%(asctime)s %(levelname)7s: %(message)s",
    datefmt="%Y/%m/%d %H:%M:%S",
    level=logging.INFO
)

MNE_USE_CUDA = 1
try:
    import mne
    mne.cuda.init_cuda(ignore_config=True, verbose=True)
    MNE_USE_CUDA = "cuda"
    logging.info("NVIDA GPU acceleration enabled.")
except ImportError as e:
    logging.info("No CUPY package found, NVIDA GPU acceleration disabled.")

from .dataset import *
from .pipeline import *

logging.getLogger().setLevel(logging.DEBUG)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
from multiprocessing import cpu_count
os.environ["NUMEXPR_MAX_THREADS"] = str(cpu_count())
