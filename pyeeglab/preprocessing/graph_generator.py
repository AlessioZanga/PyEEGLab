import os
import logging
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
        step = round(self._frequency/self._fremes)
        data = [data[t:t+step] for t in range(0, len(data), step)]
        return data

    def frameToSpearman(self, frame):
        frame = spearmanr(frame)
        return frame

    def spearmanToGraphs(self, spear):
        pass

    def dataframeToGraphs(self, data):
        data = self.dataToFrames(data)
        data = [self.frameToSpearman(frame) for frame in data]
        data = [self.spearmanToGraphs(spear) for spear in data]
        return data

    def dataframesToGraphs(self, data):
        self._logger.debug('Load EDF set to generate graphs')
        self._logger.debug('Create process pool')
        pool = Pool(len(os.sched_getaffinity(0)))
        self._logger.debug('Start process pool')
        data = pool.map(self.dataToGraphs, data)
        pool.close()
        pool.join()
        self._logger.debug('End process pool')
        return data
