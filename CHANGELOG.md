# Changelog
All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## Unreleased

## [x.y.z] - yyyy-mm-dd
### Added
### Changed
### Removed
### Fixed


## [0.9.3] - 2020-mm-dd
### Added
### Changed
### Removed
### Fixed
* HOTFIX Remove incosistent extra channel in TUH EEG Abnormal


## [0.9.2] - 2020-06-04
### Added
* DOI reference link using Zenodo
* @dataclass decorator to datadabase tables ORM
* Install instruction for Python 3.6 dataclasses

### Changed
* Renamed JoinedPreprocessor to ForkedPreprocessor
* Renamed JoinDataFrames to ToMergedDataframes
* Renamed SinglePickleCache to PickleCache

### Removed
* Python 3.6 full support due to @dataclass
    (workaround: python3.6 -m pip install dataclasses)
* Conda environment.yml configuration file
* ChunksPickleCache cache manager
* VerticalPipeline pipeline executor
* TextMiner textual analysis


## [0.9.1] - 2020-06-03
### Added
* Add min_value and max_value for each file Metadata
* Add min_value and max_value in pipeline environment variables

### Changed
* Update MinMaxNormalization and MinMaxCenteredNormalization to min/max value across samples

### Fixed
* Environment variables injection in TUH EEG Abnormal dataset


## [0.9.0] - 2020-05-25
### Added
* The CHANGELOG file.
* Initial documentation at https://pyeeglab.readthedocs.io.
* Online code editing by clicking on the GitPod badge in README.
* Travis CI support for multiple os/python configurations, including:
    * Ubuntu 16.04 Xenial / Python 3.6.0.
    * Ubuntu 18.04 Bionic / Python 3.7.0.
    * Ubuntu 18.04 Bionic / Python 3.8.0.
    * OSX 10.14 / Python 3.7.4.
    * Windows 10 / Python 3.8.0.
* Min-Max zero-centered normalization preprocessor
