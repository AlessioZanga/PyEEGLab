import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import *

class TestTUHEEGAbnormal(unittest.TestCase):
    PATH = './tests/samples/tuh_eeg_abnormal/v2.0.0/edf'

    def test_index(self):
        TUHEEGAbnormalLoader(self.PATH)

    def test_loader(self):
        loader = TUHEEGAbnormalLoader(self.PATH)
        loader.get_dataset()
        loader.get_dataset_text()
        loader.get_channels_set()
        loader.get_lowest_frequency()

    def test_dataset(self):
        dataset = TUHEEGAbnormalDataset(self.PATH)
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
