# PyEEGLab

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3874461.svg)](https://doi.org/10.5281/zenodo.3874461) [![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![Build Status](https://travis-ci.org/AlessioZanga/PyEEGLab.svg?branch=master)](https://travis-ci.org/AlessioZanga/PyEEGLab) [![Documentation Status](https://readthedocs.org/projects/pyeeglab/badge/?version=latest)](https://pyeeglab.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/AlessioZanga/PyEEGLab/branch/master/graph/badge.svg)](https://codecov.io/gh/AlessioZanga/PyEEGLab) [![Maintainability](https://api.codeclimate.com/v1/badges/c55f67ee28e9e8bd8038/maintainability)](https://codeclimate.com/github/AlessioZanga/PyEEGLab/maintainability) [![CodeFactor](https://www.codefactor.io/repository/github/alessiozanga/pyeeglab/badge)](https://www.codefactor.io/repository/github/alessiozanga/pyeeglab) [![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/AlessioZanga/PyEEGLab) 

Analyze and manipulate EEG data using PyEEGLab.

## Introduction

PyEEGLab is a python package developed to define pipeline for EEG preprocessing for a wide range of machine learning tasks. It supports set of datasets out-of-the-box and allow you to adapt your preferred one.

## How it Works

Here is a simple quickstart:

    from pyeeglab import *
    dataset = TUHEEGAbnormalDataset()
    pipeline = Pipeline([
        CommonChannelSet(),
        LowestFrequency(),
        ToDataframe(),
        MinMaxCentralizedNormalization(),
        DynamicWindow(8),
        ToNumpy()
    ])
    dataset = dataset.set_pipeline(preprocessing).load()
    data, labels = dataset['data'], dataset['labels']

In this example, for each sample in the dataset, a common set of electrodes is selected, then downsampled to the lowest frequency and normalized using a min-max centralized approach. Each sample is then splitted in eight windows or frames.

This approach is quite usefull for tasks like artifact classification or seizure detection.

## How to Install

PyEEGLab is distributed using the pip repository:

    pip install PyEEGLab

If you use Python 3.6, the dataclasses package must be installed as backport of Python 3.7 dataclasses:

    pip install dataclasses

If you need a bleeding edge version, you can install it directly from GitHub:

    pip install git+https://github.com/AlessioZanga/PyEEGLab@develop

## Out-Of-The-Box Supported Datasets

The following datasets will work upon downloading:

* [Temple University Abnormal EEG Dataset](https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml)
* [Temple University Artifact EEG Dataset](https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml)
* [EEG Motor Movement/Imagery Dataset](https://physionet.org/content/eegmmidb/1.0.0/)

## How to Get a Dataset

> **WARNING (1)**: Retriving the TUH EEG Abnormal dataset require at least 65GB of free disk space.

> **WARNING (2)**: Retriving the TUH EEG Abnormal dataset require valid credentials, you can get your own at https://www.isip.piconepress.com/projects/tuh_eeg/html/request_access.php.

In the root directory of this project there is a Makefile, by typing:

    make tuh_eeg_abnormal

you will trigger the dataset download.

## Documentation

> **WIP**: Documentation is currently Work-In-Progress, if you need additional info, please, contact me directly.

You can find the documentation at https://pyeeglab.readthedocs.io

## Credits

If you use this code in your project use the citation below:

    @misc{Zanga2019PyEEGLab,
        title={PyEEGLab: A simple tool for EEG manipulation},
        author={Alessio Zanga},
        year={2019},
        doi={10.5281/zenodo.3874461},
        url={https://dx.doi.org/10.5281/zenodo.3874461},
        howpublished={\url{https://github.com/AlessioZanga/PyEEGLab}},
    }

## Related publications

- "An Attention-based Architecture for EEG Classification" - https://doi.org/10.5220/0008953502140219
