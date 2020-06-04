import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import EEGMMIDBLoader, EEGMMIDBDataset, \
                     Pipeline, CommonChannelSet, LowestFrequency, BandPassFrequency, ToDataframe, \
                     DynamicWindow, ForkedPreprocessor, BinarizedSpearmanCorrelation, \
                     CorrelationToAdjacency, Bandpower, GraphWithFeatures

class TestEEGMMIDB(unittest.TestCase):
    PATH = './tests/samples/physionet.org/files/eegmmidb/1.0.0'

    def test_index(self):
        EEGMMIDBLoader(self.PATH)

    def test_loader(self):
        loader = EEGMMIDBLoader(self.PATH)
        loader.get_dataset()
        loader.get_dataset_text()
        loader.get_channelset()
        loader.get_lowest_frequency()

    def test_dataset(self):
        dataset = EEGMMIDBDataset(self.PATH)
        preprocessing = Pipeline([
            CommonChannelSet(),
            LowestFrequency(),
            BandPassFrequency(0.1, 47),
            ToDataframe(),
            DynamicWindow(4),
            ForkedPreprocessor(
                inputs=[
                    [BinarizedSpearmanCorrelation(), CorrelationToAdjacency()],
                    Bandpower()
                ],
                output=GraphWithFeatures()
            )
        ])
        dataset = dataset.set_pipeline(preprocessing).load()
