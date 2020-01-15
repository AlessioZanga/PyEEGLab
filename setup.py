import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='PyEEGLab',
    version='0.7.1',
    author='Alessio Zanga',
    author_email='alessio.zanga@outlook.it',
    license='GNU GENERAL PUBLIC LICENSE - Version 3, 29 June 2007',
    description='Analyze and manipulate EEG data using PyEEGLab',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/AlessioZanga/PyEEGLab',
    packages=setuptools.find_packages(),
    install_requires=[
        'numpy',
        'pandas',
        'nltk',
        'networkx>=2.2',
        'mne>=0.19',
        'wfdb',
        'yasa>=0.1.7',
        'sqlalchemy>=1.2',
    ],
)
