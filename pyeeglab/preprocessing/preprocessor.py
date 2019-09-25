from os import sched_getaffinity
from os.path import join, isfile
from typing import List
from multiprocessing import Pool
import uuid
import pickle
import logging
import pandas as pd

from .graph_generator import GraphGenerator
from ..io.raw import Raw


class Preprocessor():

    def __init__(self, shift: int, tmax: int, chs: List[str], freq: float) -> None:
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
        self.frames = 0

    def set_bandpass_frequency(self, l_freq: float, h_freq: float) -> None:
        logging.debug('Set data preprocessor band to %s/%s Hz ', l_freq, h_freq)
        self.low_frequency = l_freq
        self.high_frequency = h_freq

    def set_frames(self, frames: int) -> None:
        logging.debug('Set data preprocessor frames to %s', frames)
        self.frames = frames

    def get_sign(self, count, type, c=0, p1=0, p2=0):
        return 'data_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}.pkl'.format(
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
            type
        )

    def load_data(self, export, sign):
        path = join(export, sign)
        if isfile(path):
            logging.debug('Load data from %s', path)
            with open(path, 'rb') as file:
                data = pickle.load(file)
            return data
        return None

    def save_data(self, export, sign, data):
        path = join(export, sign)
        logging.debug('Save data to %s', path)
        with open(path, 'wb') as file:
            pickle.dump(data, file)

    def _normalize(self, data: Raw) -> pd.DataFrame:
        with data.open() as reader:
            data.set_tmax(self.tmax, self.shift)
            logging.debug('Load %s data for processing', data.id)
            reader.load_data()
            data.set_channels(self.channels)
            data.set_frequency(self.frequency, self.low_frequency, self.high_frequency)
            return reader.to_data_frame()[:self.tmax * self.frequency]

    def normalize(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'norm')
        logging.debug('Get data %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.map(self._normalize, data)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data

    def _get_frames(self, data):
        data = self._normalize(data)
        grapher = GraphGenerator(self.frequency, self.frames)
        return grapher.data_to_frames(data)

    def get_frames(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'frames')
        logging.debug('Get frames %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.map(self._get_frames, data)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data

    def _get_correlations(self, data):
        data = self._normalize(data)
        grapher = GraphGenerator(self.frequency, self.frames)
        frames = grapher.data_to_frames(data)
        correlations = [grapher.frame_to_correlation(frame) for frame in frames]
        return correlations

    def get_correlations(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'correlations')
        logging.debug('Get correlations %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.map(self._get_correlations, data)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data

    def _get_adjs(self, data, c, p1, p2):
        data = self._normalize(data)
        grapher = GraphGenerator(self.frequency, self.frames)
        return grapher.dataframe_to_graphs(data, c, p1, p2, True)

    def get_adjs(self, data, labels, c, p1, p2, export=None):
        sign = self.get_sign(len(data), 'adjs', c, p1, p2)
        logging.debug('Get adjs %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        params = zip(
            data,
            [c] * len(data),
            [p1] * len(data),
            [p2] * len(data)
        )
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.starmap(self._get_adjs, params)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data

    def _get_weighted_adjs(self, data):
        data = self._normalize(data)
        grapher = GraphGenerator(self.frequency, self.frames)
        return grapher.dataframe_to_graphs(data, 0, 0, 0, True, True)

    def get_weighted_adjs(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'weightedadjs')
        logging.debug('Get adjs %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.map(self._get_weighted_adjs, data)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data

    def _get_graphs(self, data, c, p1, p2, node_features):
        data = self._normalize(data)
        grapher = GraphGenerator(self.frequency, self.frames)
        return grapher.dataframe_to_graphs(data, c, p1, p2, node_features=node_features)

    def get_graphs(self, data, labels, c, p1, p2, node_features, export=None):
        sign = self.get_sign(len(data), 'graphs', c, p1, p2)
        logging.debug('Get graphs %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        params = zip(
            data,
            [c] * len(data),
            [p1] * len(data),
            [p2] * len(data),
            [node_features] * len(data)
        )
        pool = Pool(len(sched_getaffinity(0)))
        data = pool.starmap(self._get_graphs, params)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data
