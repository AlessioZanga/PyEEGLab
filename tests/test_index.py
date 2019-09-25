import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pyeeglab

def test_index():
    index = pyeeglab.TUHEEGCorpusLoader('./tests/samples')
