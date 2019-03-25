import logging
from importlib.util import find_spec


class Normalizer():
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

    def normalize(self, data):
        data.open()
        data.setTMax(self.getTMax())
        self._logger.debug('Load %s data for processing', data.id())
        data.reader().load_data()
        data.setChannels(self.getChannels())
        freq = data.reader().info['sfreq']
        if freq > self.getFrequency():
            self._logger.debug(
                'Downsample %s from %s to %s', data.id(), freq, self.getFrequency()
            )
            n_jobs = 1
            if find_spec('cupy') is not None:
                self._logger.debug('Load CUDA Cores for processing %s', data.id())
                n_jobs = 'cuda'
            data.reader().resample(self.getFrequency(), n_jobs=n_jobs)
        return data
