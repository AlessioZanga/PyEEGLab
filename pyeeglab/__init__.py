import logging
import warnings

logging.basicConfig(format="%(asctime)s %(levelname)7s: %(message)s", datefmt="%Y/%m/%d %H:%M:%S")

from .dataset import *
from .pipeline import *

logging.getLogger().setLevel(logging.DEBUG)
warnings.filterwarnings("ignore", category=RuntimeWarning)
warnings.filterwarnings("ignore", category=UserWarning)

import os
from multiprocessing import cpu_count
os.environ["NUMEXPR_MAX_THREADS"] = str(cpu_count())
