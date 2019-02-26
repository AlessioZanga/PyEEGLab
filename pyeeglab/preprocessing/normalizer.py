import os
import logging
from importlib.util import find_spec
from multiprocessing import Pool


class DataNormalizer():
    _tmax = None
    _channels = None
    _frequency = None
    _logger = logging.getLogger()

    def __init__(self, tmax, chs, freq):
        self._logger.debug('Create data normalizer')
        self._logger.debug('Set data normalizer time to %s seconds', tmax)
        self._tmax = tmax
        self._logger.debug('Set data normalizer channels to %s', '|'.join(chs))
        self._channels = chs
        self._logger.debug('Set data normalizer frequency to %s Hz', freq)
        self._frequency = freq

    def getTMax(self):
        return self._tmax

    def getChannels(self):
        return self._channels

    def getFrequency(self):
        return self._frequency

    def EDFNormalize(self, edf):
        edf.open()
        edf.setTMax(self.getTMax())
        self._logger.debug('Load EDF %s data for processing', edf.getId())
        edf.reader().load_data()
        edf.setChannels(self.getChannels())
        freq = edf.reader().info['sfreq']
        if freq > self.getFrequency():
            self._logger.debug(
                'Downsample EDF %s from %s to %s', edf.getId(), freq, self.getFrequency()
            )
            n_jobs = 1
            if find_spec('cupy') is not None:
                self._logger.debug('Load CUDA Cores for processing %s', edf.getId())
                n_jobs = 'cuda'
            edf.reader().resample(self.getFrequency(), n_jobs=n_jobs)
        return edf

    def EDFSNormalize(self, edfs):
        self._logger.debug('Load EDF set for normalizing')
        self._logger.debug('Create process pool')
        pool = Pool(len(os.sched_getaffinity(0)))
        self._logger.debug('Start process pool')
        edfs = pool.map(self.EDFNormalize, edfs)
        pool.close()
        pool.join()
        self._logger.debug('End process pool')
        return edfs
