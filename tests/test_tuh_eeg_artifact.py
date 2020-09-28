import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import *

class TestTUHEEGArtifact(unittest.TestCase):
    PATH = './tests/samples/tuh_eeg_artifact/'

    def test_index(self):
        TUHEEGArtifactDataset(self.PATH)

    def test_loader(self):
        loader = TUHEEGArtifactDataset(self.PATH)
        loader.maximal_channels_subset
        loader.lowest_frequency
        loader.signal_min_max_range

    def test_dataset(self):
        dataset = TUHEEGArtifactDataset(self.PATH)
        preprocessing = Pipeline([
            CommonChannelSet(),
            LowestFrequency(),
            BandPassFrequency(0.1, 47),
            ToDataframe(),
            DynamicWindow(4),
            Skewness(),
            ToNumpy()
        ])
        dataset = dataset.set_pipeline(preprocessing).load()
