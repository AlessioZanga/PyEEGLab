import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import *

class TestCHBMIT(unittest.TestCase):
    PATH = './tests/samples/physionet.org/files/chbmit/'

    def test_index(self):
        PhysioNetCHBMITDataset(self.PATH)

    def test_loader(self):
        loader = PhysioNetCHBMITDataset(self.PATH)
        loader.maximal_channels_subset
        loader.lowest_frequency

    def test_dataset(self):
        dataset = PhysioNetCHBMITDataset(self.PATH)
        preprocessing = Pipeline([
            CommonChannelSet(),
            LowestFrequency(),
            BandPassFilter(0.1, 47),
            ToDataframe(),
            DynamicWindow(4),
            Skewness(),
            ToNumpy()
        ])
        dataset = dataset.set_pipeline(preprocessing).load()
