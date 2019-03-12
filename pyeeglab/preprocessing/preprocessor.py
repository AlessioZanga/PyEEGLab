from .normalizer import DataNormalizer
from .graph_generator import GraphGenerator

import os
import uuid
import pickle
from multiprocessing import Pool


class Preprocessor():

    def __init__(self, tmax, channels, frequency, frames):
        self._t = tmax
        self._ch = channels
        self._f = frequency
        self._n = frames

    def getSign(self, count, type, c=0, p1=0, p2=0):
        return 'data_{0}_{1}_{2}_{3}_{4}_{5}_{6}_{7}_{8}.pkl'.format(
            count,
            self._t,
            str(uuid.uuid5(uuid.NAMESPACE_X500, '-'.join(self._ch))),
            self._f,
            self._n,
            c,
            p1,
            p2,
            type
        )

    def loadData(self, export, sign):
        path = os.path.join(export, sign)
        if os.path.isfile(path):
            # print('Loading data {}'.format(path))
            with open(path, 'rb') as file:
                data = pickle.load(file)
            return data
        return None

    def saveData(self, export, sign, data):
        path = os.path.join(export, sign)
        with open(path, 'wb') as file:
            pickle.dump(data, file)

    def _getFrames(self, data):
        normalizer = DataNormalizer(self._t, self._ch, self._f)
        data = normalizer.EDFNormalize(data)
        data = data.reader().to_data_frame()[:self._t * self._f]
        grapher = GraphGenerator(self._f, self._n)
        return grapher.dataToFrames(data)

    def getFrames(self, data, labels, export=None):
        sign = self.getSign(len(data), 'frames')
        if export is not None:
            load = self.loadData(export, sign)
            if load is not None:
                return load
        pool = Pool(len(os.sched_getaffinity(0)))
        data = pool.map(self._getFrames, data)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.saveData(export, sign, data)
        return data

    def _getAdjs(self, data, c, p1, p2):
        normalizer = DataNormalizer(self._t, self._ch, self._f)
        data = normalizer.EDFNormalize(data)
        data = data.reader().to_data_frame()[:self._t * self._f]
        grapher = GraphGenerator(self._f, self._n)
        return grapher.dataframeToGraphs(data, c, p1, p2, True)

    def getAdjs(self, data, labels, c, p1, p2, export=None):
        sign = self.getSign(len(data), 'adjs', c, p1, p2)
        if export is not None:
            load = self.loadData(export, sign)
            if load is not None:
                return load
        params = zip(
            data,
            [c] * len(data),
            [p1] * len(data),
            [p2] * len(data)
        )
        pool = Pool(len(os.sched_getaffinity(0)))
        data = pool.starmap(self._getAdjs, params)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.saveData(export, sign, data)
        return data

    def _getGraphs(self, data, c, p1, p2):
        normalizer = DataNormalizer(self._t, self._ch, self._f)
        data = normalizer.EDFNormalize(data)
        data = data.reader().to_data_frame()[:self._t * self._f]
        grapher = GraphGenerator(self._f, self._n)
        return grapher.dataframeToGraphs(data, c, p1, p2)

    def getGraphs(self, data, labels, c, p1, p2, export=None):
        sign = self.getSign(len(data), 'graphs', c, p1, p2)
        if export is not None:
            load = self.loadData(export, sign)
            if load is not None:
                return load
        params = zip(
            data,
            [c] * len(data),
            [p1] * len(data),
            [p2] * len(data)
        )
        pool = Pool(len(os.sched_getaffinity(0)))
        data = pool.starmap(self._getGraphs, params)
        pool.close()
        pool.join()
        data = {
            'labels': labels,
            'data': data
        }
        if export is not None:
            self.saveData(export, sign, data)
        return data
