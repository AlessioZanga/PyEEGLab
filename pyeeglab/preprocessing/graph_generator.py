import os
import logging
import numpy as np
from scipy.stats import spearmanr
from multiprocessing import Pool


class GraphGenerator():
    _logger = logging.getLogger()

    def __init__(self, freq, fps):
        self._logger.debug('Create graph generator')
        self._logger.debug('Set graph generator frequency to %s Hz', freq)
        self._frequency = freq
        self._logger.debug('Set graph generator frame per seconds to %s', fps)
        self._frames = fps

    def dataToFrames(self, data):
        step = round(self._frequency/self._frames)
        data = [data[t:t+step] for t in range(0, len(data), step)]
        return data

    def frameToCorrelation(self, frame):
        frame = spearmanr(frame)
        return frame.correlation

    def filterCorrelation(self, corr, upper, lower):
        if corr > upper or corr < lower:
            return 1
        return 0

    def correlationsToAdjacencies(self, data, c, p1, p2):
        rows = list(range(data[0].shape[0]))
        columns = list(range(data[0].shape[1]))
        q = [
            [
                [data[k][i][j] for k in range(len(data))]
                for j in columns
            ]
            for i in rows
        ]
        q = [
            [
                [np.percentile(q[i][j], p1), np.percentile(q[i][j], p2)]
                for j in range(len(q[i]))
            ]
            for i in range(len(q))
        ]
        data = [
            [
                [
                    self.filterCorrelation(
                        data[k][i][j],
                        max(c, q[i][j][1]),
                        min(-c, q[i][j][0])
                    )
                    for j in columns
                ]
                for i in rows
            ]
            for k in range(len(data))
        ]
        return data

    def adjacencyToGraph(self, adj):
        pass

    def dataframeToGraphs(self, data, c, p1, p2):
        data = self.dataToFrames(data)
        data = [self.frameToCorrelation(frame) for frame in data]
        data = self.correlationsToAdjacencies(data, c, p1, p2)
        data = [self.correlationToGraph(corr) for corr in data]
        return data

    def dataframesToGraphs(self, data, c, p1, p2):
        self._logger.debug('Load EDF set to generate graphs')
        self._logger.debug('Create process pool')
        pool = Pool(len(os.sched_getaffinity(0)))
        self._logger.debug('Start process pool')
        data = list(zip(data, [c]*len(data), [p1]*len(data), [p2]*len(data)))
        data = pool.starmap(self.dataframeToGraphs, data)
        pool.close()
        pool.join()
        self._logger.debug('End process pool')
        return data
