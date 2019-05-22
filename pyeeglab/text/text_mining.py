import os
from multiprocessing import Pool
from nltk import word_tokenize, LancasterStemmer
from nltk.corpus import stopwords


class TextMiner():
    def __init__(self, dataset):
        self._dataset = {}
        for key, value in dataset.items():
            with open(value[0], 'r', encoding='utf8', errors='replace') as file:
                text = file.read()
                text = text.replace('\n', ' ').strip()
                self._dataset[key] = (text, value[1])

    def getDataset(self):
        return self._dataset

    def getDatasetAbnormal(self):
        data = {
            key: value
            for key, value in self._dataset.items()
            if value[1] == 'abnormal'
        }
        return data

    def getNormalizedDataset(self):
        data = self.normalize()
        return data

    def getNormalizedAbnormalDataset(self):
        data = self.normalize()
        data = {
            key: value
            for key, value in data.items()
            if value[1] == 'abnormal'
        }
        return data

    def _normalize(self, item):
        key, value = item
        ls = LancasterStemmer()
        text = word_tokenize(value[0])
        text = [word.lower() for word in text]
        text = [
            ls.stem(word).rstrip('s')
            for word in text
            if word not in stopwords.words('english') and word.isalnum()
        ]
        return (key, (text, value[1]))

    def normalize(self):
        items = list(self._dataset.items())
        pool = Pool(len(os.sched_getaffinity(0)))
        items = pool.map(self._normalize, items)
        pool.close()
        pool.join()
        return dict(items)
