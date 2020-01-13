import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import TextMiner, TUHEEGAbnormalLoader, TUHEEGAbnormalDataset, \
                     Pipeline, CommonChannelSet, LowestFrequency, BandPassFrequency, ToDataframe, \
                     DynamicWindow, ToNumpy

PATH = './tests/samples/tuh_eeg_abnormal/v2.0.0/edf'

def test_index():
    TUHEEGAbnormalLoader(PATH)

def test_loader():
    loader = TUHEEGAbnormalLoader(PATH)
    print(loader.get_dataset())
    print(loader.get_dataset_text())
    print(loader.get_channelset())
    print(loader.get_lowest_frequency())

def test_dataset():
    dataset = TUHEEGAbnormalDataset(PATH)
    preprocessing = Pipeline([
        CommonChannelSet(),
        LowestFrequency(),
        BandPassFrequency(0.1, 47),
        ToDataframe(),
        DynamicWindow(4),
        ToNumpy()
    ])
    dataset = dataset.set_pipeline(preprocessing).load()

def test_text_miner():
    loader = TUHEEGAbnormalLoader(PATH)
    text = loader.get_dataset_text()
    miner = TextMiner(text)
    print(miner.get_dataset())
