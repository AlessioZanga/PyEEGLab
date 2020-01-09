import os
import sys
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from pyeeglab import TextMiner, TUHEEGArtifactLoader, TUHEEGArtifactDataset, \
                     Pipeline, CommonChannelSet, LowestFrequency, BandPassFrequency, ToDataframe, \
                     DynamicWindow

PATH = './tests/samples/tuh_eeg_artifact/v1.0.0/edf'

def test_index():
    TUHEEGArtifactLoader(PATH)

def test_loader():
    loader = TUHEEGArtifactLoader(PATH)
    print(loader.get_dataset())
    print(loader.get_dataset_text())
    print(loader.get_channelset())
    print(loader.get_lowest_frequency())

def test_dataset():
    dataset = TUHEEGArtifactDataset(PATH)
    preprocessing = Pipeline([
        CommonChannelSet(),
        LowestFrequency(),
        BandPassFrequency(0.1, 48),
        ToDataframe(),
        DynamicWindow(4)
    ])
    dataset = dataset.set_pipeline(preprocessing).load()

def test_text_miner():
    loader = TUHEEGArtifactLoader(PATH)
    text = loader.get_dataset_text()
    miner = TextMiner(text)
    print(miner.get_dataset())
