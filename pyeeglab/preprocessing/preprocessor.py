import os
import uuid
import pickle
import logging
from multiprocessing import Pool
import numpy as np

from .normalizer import Normalizer
from .graph_generator import GraphGenerator


class Preprocessor():
    _logger = logging.getLogger()

    def __init__(self, shift, tmax, chs, freq, l_freq, h_freq, frame):
        self._logger.debug('Create data preprocessor')
        self._logger.debug('Set data preprocessor shift time to %s seconds', shift)
        self._shift = shift
        self._logger.debug('Set data preprocessor time to %s seconds', tmax)
        self._tmax = tmax
        self._logger.debug('Set data preprocessor channels to %s', '|'.join(chs))
        self._channels = chs
        self._logger.debug('Set data preprocessor frequency to %s Hz', freq)
        self._frequency = freq
        self._logger.debug('Set data normalizer band to %s/%s Hz ', l_freq, h_freq)
        self._low_frequency = l_freq
        self._high_frequency = h_freq
        self._logger.debug('Set data preprocessor frames to %s', frame)
        self._frames = frame

    def get_sign(self, count, type, c=0, p1=0, p2=0):
        return 'data_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}_{9}_{10}_{11}.pkl'.format(
            count,
            self._shift,
            self._tmax,
            str(uuid.uuid5(uuid.NAMESPACE_X500, '-'.join(self._channels))),
            self._frequency,
            self._low_frequency,
            self._high_frequency,
            self._frames,
            c,
            p1,
            p2,
            type
        )

    def load_data(self, export, sign):
        path = os.path.join(export, sign)
        if os.path.isfile(path):
            self._logger.debug('Load data from %s', path)
            with open(path, 'rb') as file:
                data = pickle.load(file)
            return data
        return None

    def save_data(self, export, sign, data):
        path = os.path.join(export, sign)
        self._logger.debug('Save data to %s', path)
        with open(path, 'wb') as file:
            pickle.dump(data, file)

    def _normalize(self, data):
        normalizer = Normalizer(self._shift, self._tmax, self._channels, self._frequency, self._low_frequency, self._high_frequency)
        data = normalizer.normalize(data)
        data = data.reader().to_data_frame()[:self._tmax * self._frequency]
        return data

    def normalize(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'norm')
        self._logger.debug('Get data %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(os.sched_getaffinity(0)))
        data = pool.map(self._normalize, data)
        pool.close()
        pool.join()
        data = np.array([d.values for d in data]).astype('float32')
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.save_data(export, sign, data)
        return data

    def _get_frames(self, data):
        data = self._normalize(data)
        grapher = GraphGenerator(self._frequency, self._frames)
        return grapher.data_to_frames(data)

    def get_frames(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'frames')
        self._logger.debug('Get frames %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(os.sched_getaffinity(0)))
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
        grapher = GraphGenerator(self._frequency, self._frames)
        frames = grapher.data_to_frames(data)
        correlations = [grapher.frame_to_correlation(frame) for frame in frames]
        return correlations
    
    def get_correlations(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'correlations')
        self._logger.debug('Get correlations %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(os.sched_getaffinity(0)))
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
        grapher = GraphGenerator(self._frequency, self._frames)
        return grapher.dataframe_to_graphs(data, c, p1, p2, True)

    def get_adjs(self, data, labels, c, p1, p2, export=None):
        sign = self.get_sign(len(data), 'adjs', c, p1, p2)
        self._logger.debug('Get adjs %s', sign)
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
        pool = Pool(len(os.sched_getaffinity(0)))
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
        grapher = GraphGenerator(self._frequency, self._frames)
        return grapher.dataframe_to_graphs(data, 0, 0, 0, True, True)

    def get_weighted_adjs(self, data, labels, export=None):
        sign = self.get_sign(len(data), 'weightedadjs')
        self._logger.debug('Get adjs %s', sign)
        if export is not None:
            load = self.load_data(export, sign)
            if load is not None:
                return load
        pool = Pool(len(os.sched_getaffinity(0)))
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

    def _get_graphs(self, data, c, p1, p2):
        data = self._normalize(data)
        grapher = GraphGenerator(self._frequency, self._frames)
        return grapher.dataframe_to_graphs(data, c, p1, p2)

    def get_graphs(self, data, labels, c, p1, p2, export=None):
        sign = self.get_sign(len(data), 'graphs', c, p1, p2)
        self._logger.debug('Get graphs %s', sign)
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
        pool = Pool(len(os.sched_getaffinity(0)))
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
