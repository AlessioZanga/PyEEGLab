from os import sched_getaffinity
from os.path import join, isfile
from typing import List
from multiprocessing import Pool
import uuid
import pickle
import logging
from numpy import ndarray
from pandas import DataFrame
from networkx import Graph

from .graph_generator import GraphGenerator
from ..io.raw import Raw


class Preprocessor():

    def __init__(self, shift: int, tmax: int, chs: List[str], freq: float, frames: int) -> None:
        logging.debug('Create data preprocessor')
        logging.debug('Set data preprocessor shift time to %s seconds', shift)
        self.shift = shift
        logging.debug('Set data preprocessor time to %s seconds', tmax)
        self.tmax = tmax
        logging.debug('Set data preprocessor channels to %s', '|'.join(chs))
        self.channels = chs
        logging.debug('Set data preprocessor frequency to %s Hz', freq)
        self.frequency = freq
        self.low_frequency = 0
        self.high_frequency = 0
        logging.debug('Set data preprocessor frames to %s', frames)
        self.frames = frames
        self.grapher = GraphGenerator(self.frequency, self.frames)

    def set_bandpass_frequency(self, l_freq: float, h_freq: float) -> None:
        logging.debug('Set data preprocessor band to %s/%s Hz ', l_freq, h_freq)
        self.low_frequency = l_freq
        self.high_frequency = h_freq

    def get_sign(self, count: int, mode: str, c: float = 0, p1: int = 0, p2: float = 0, node_features: bool = False) -> str:
        return 'data_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}_{12}.pkl'.format(
            count,
            self.shift,
            self.tmax,
            str(uuid.uuid5(uuid.NAMESPACE_X500, '-'.join(self.channels))),
            self.frequency,
            self.low_frequency,
            self.high_frequency,
            self.frames,
            c,
            p1,
            p2,
            node_features,
            mode
        )

    def load_data(self, export: str, sign: str):
        path = join(export, sign)
        if isfile(path):
            logging.debug('Load data from %s', path)
            with open(path, 'rb') as file:
                data = pickle.load(file)
            return data
        return None

    def save_data(self, export: str, sign: str, data):
        path = join(export, sign)
        logging.debug('Save data to %s', path)
        with open(path, 'wb') as file:
            pickle.dump(data, file)

    def _get_normalized(self, data: Raw, *args) -> DataFrame:
        with data.open() as reader:
            if (self.tmax >= 0 and self.shift >= 0):
                data.set_tmax(self.tmax, self.shift)
            logging.debug('Load %s data for processing', data.id)
            reader.load_data()
            data.set_channels(self.channels)
            data.set_frequency(self.frequency, self.low_frequency, self.high_frequency)
            return reader.to_data_frame()[:self.tmax * self.frequency]

    def _get_frames(self, data: Raw, *args) -> List[ndarray]:
        data = self._get_normalized(data)
        frames = self.grapher.data_to_frames(data)
        return [frame.to_numpy() for frame in frames]

    def _get_correlations(self, data: Raw, *args) -> List[ndarray]:
        data = self._get_normalized(data)
        frames = self.grapher.data_to_frames(data)
        return [self.grapher.frame_to_correlation(frame).to_numpy() for frame in frames]

    def _get_adjs(self, data: Raw, c: float, p1: int, p2: int, *args):
        data = self._get_normalized(data)
        return self.grapher.dataframe_to_graphs(data, c, p1, p2, True)

    def _get_weighted_adjs(self, data: Raw, *args):
        data = self._get_normalized(data)
        return self.grapher.dataframe_to_graphs(data, 0, 0, 0, True, True)

    def _get_graphs(self, data: Raw, c: float, p1: int, p2: int, node_features: bool) -> List[Graph]:
        data = self._get_normalized(data)
        return self.grapher.dataframe_to_graphs(data, c, p1, p2, node_features=node_features)        

    # Modes: normalized, frames, correlations, adjs, weighted_adjs, graphs

    def load(self, mode, data, labels, c: float = 0, p1: int = 0, p2: int = 0, node_features: bool = False, export: str = None):
        sign = self.get_sign(len(data), mode, c, p1, p2, node_features)
        logging.debug('Get %s %s', mode, sign)
        if export is not None:
            dataset = self.load_data(export, sign)
            if dataset is not None:
                return dataset
        params = zip(
            data,
            [c] * len(data),
            [p1] * len(data),
            [p2] * len(data),
            [node_features] * len(data)
        )
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.starmap(getattr(self, '_get_' + mode), params)
        pool.close()
        pool.join()
        if self.frames < 1:
            data = [d[0] for d in data]
        dataset = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, dataset)
        return dataset
