import os
import pytest
from zipfile import ZipFile

@pytest.fixture(scope='session', autouse=True)
def initializer():
    if 'initialized' not in globals():
        os.system('cat tests/samples.z* > tests/samples.zip')
        with ZipFile('tests/samples.zip', 'r') as file:
            file.extractall('tests/')
        globals()['initialized'] = True
