import logging
import json

from abc import ABC, abstractmethod
from hashlib import md5

from typing import List


class Preprocessor(ABC):

    def __init__(self) -> None:
        logging.debug('Create new preprocessor')

    @abstractmethod
    def run(self, data, **kwargs):
        pass

    def to_json(self) -> str:
        out = {self.__class__.__name__: {}}
        out = json.dumps(out)
        return out

    def __eq__(self, other):
        return hash(self) == hash(other)

    def __hash__(self):
        out = md5(self.to_json()).hexdigest()
        out = int(out, 16)
        return out


class ForkedPreprocessor(Preprocessor):

    def __init__(self, inputs: List, output: Preprocessor) -> None:
        super().__init__()
        logging.debug('Create new forked preprocessor')
        self.inputs = inputs
        self.output = output

    def run(self, data, **kwargs):
        results = []
        for item in self.inputs:
            if isinstance(item, list):
                result = data
                for preprocessor in item:
                    result = preprocessor.run(result, **kwargs)
            if isinstance(item, Preprocessor):
                result = item.run(data, **kwargs)
            results.append(result)
        data = self.output.run(results, **kwargs)
        return data

    def to_json(self) -> str:
        inputs_json = []
        for i in self.inputs:
            if isinstance(i, list):
                j = [json.loads(p.to_json()) for p in i]
            if isinstance(i, Preprocessor):
                j = json.loads(i.to_json())
            inputs_json.append(j)
        output_json = json.loads(self.output.to_json())
        output_json = {
            self.__class__.__name__: {
                'inputs': inputs_json,
                'output': output_json
            }
        }
        output_json = json.dumps(output_json)
        return output_json
