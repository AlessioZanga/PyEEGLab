import logging
from importlib.util import find_spec


class Normalizer():
    _logger = logging.getLogger()

    def __init__(self, shift, tmax, chs, freq, l_freq, h_freq):
        self._logger.debug('Create data normalizer')
        self._logger.debug('Set data normalizer shift time to %s seconds', shift)
        self._shift = shift
        self._logger.debug('Set data normalizer time to %s seconds', tmax)
        self._tmax = tmax
        self._logger.debug('Set data normalizer channels to %s', '|'.join(chs))
        self._channels = chs
        self._logger.debug('Set data normalizer frequency to %s Hz', freq)
        self._frequency = freq
        self._logger.debug('Set data normalizer band to %s/%s Hz ', l_freq, h_freq)
        self._low_frequency = l_freq
        self._high_frequency = h_freq

    def get_shift(self):
        return self._shift

    def get_tmax(self):
        return self._tmax

    def get_channels(self):
        return self._channels

    def get_frequency(self):
        return self._frequency

    def normalize(self, data):
        data.open()
        data.set_tmax(self.get_tmax(), self.get_shift())
        self._logger.debug('Load %s data for processing', data.id())
        data.reader().load_data()
        data.set_channels(self.get_channels())
        freq = data.reader().info['sfreq']
        if freq > self.get_frequency():
            self._logger.debug(
                'Downsample %s from %s to %s', data.id(), freq, self.get_frequency()
            )
            n_jobs = 1
            if find_spec('cupy') is not None:
                self._logger.debug('Load CUDA Cores for processing %s', data.id())
                n_jobs = 'cuda'
            if self._low_frequency > 0 and self._high_frequency > 0:
                data.reader().filter(self._low_frequency, self._high_frequency, n_jobs=n_jobs)
            data.reader().resample(self.get_frequency(), n_jobs=n_jobs)
        return data
