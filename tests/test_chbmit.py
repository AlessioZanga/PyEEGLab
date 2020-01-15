import os
import sys
import unittest
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import TextMiner, CHBMITLoader, CHBMITDataset, \
                     Pipeline, CommonChannelSet, LowestFrequency, BandPassFrequency, ToDataframe, \
                     DynamicWindow, JoinedPreprocessor, BinarizedSpearmanCorrelation, \
                     CorrelationToAdjacency, Bandpower, GraphWithFeatures

class TestCHBMIT(unittest.TestCase):
    PATH = './tests/samples/physionet.org/files/chbmit/1.0.0'

    def test_index(self):
        CHBMITLoader(self.PATH)

    def test_loader(self):
        loader = CHBMITLoader(self.PATH)
        loader.get_dataset()
        loader.get_dataset_text()
        loader.get_channelset()
        loader.get_lowest_frequency()

    def test_dataset(self):
        dataset = CHBMITDataset(self.PATH)
        preprocessing = Pipeline([
            CommonChannelSet(),
            LowestFrequency(),
            BandPassFrequency(0.1, 47),
            ToDataframe(),
            DynamicWindow(4),
            JoinedPreprocessor(
                inputs=[
                    [BinarizedSpearmanCorrelation(), CorrelationToAdjacency()],
                    Bandpower()
                ],
                output=GraphWithFeatures()
            )
        ])
        dataset = dataset.set_pipeline(preprocessing).load()

    def test_text_miner(self):
        loader = CHBMITLoader(self.PATH)
        text = loader.get_dataset_text()
        miner = TextMiner(text)
        miner.get_dataset()
