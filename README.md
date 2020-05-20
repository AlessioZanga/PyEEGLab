# PyEEGLab

[![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![Build Status](https://travis-ci.org/AlessioZanga/PyEEGLab.svg?branch=master)](https://travis-ci.org/AlessioZanga/PyEEGLab) [![codecov](https://codecov.io/gh/AlessioZanga/PyEEGLab/branch/master/graph/badge.svg)](https://codecov.io/gh/AlessioZanga/PyEEGLab) [![Maintainability](https://api.codeclimate.com/v1/badges/c55f67ee28e9e8bd8038/maintainability)](https://codeclimate.com/github/AlessioZanga/PyEEGLab/maintainability)

Analyze and manipulate EEG data using PyEEGLab.

## Introduction

PyEEGLab is a python package developed to extract multiple adjacent EEGs sections, called *frames*, from a set of EEGs records. Each frame is processed in order to create a *graph representation* of brain's activity, expressed as interaction between pairs of electrodes. Furthermore, each node of a graph has its own set of features, computed using the average power of five different frequency bands.  

The result is a series of ordered lists of graphs, where each list is associated to a patient. Each patient's EEG is classified as 'normal' or 'abnormal', so our goal is to create a **binary classifier** using this data representation.  

It is possible to extract others data representations using different configurations of this package. Although it is not directly implemented, this project was structured to allow processing differents datasets, not only the TUH EGG Abnormal, by reimplementing the Index, Loader and Dataset classes.

## How to Install

PyEEGLab is distributed using the pip repository:

    pip install PyEEGLab

If you need a bleeding edge version, you can install it directly from GitHub:

    pip install git+https://github.com/AlessioZanga/PyEEGLab@develop

## How to get the TUH EEG Abnormal dataset

> **WARNING (1)**: Retriving the TUH EEG Abnormal dataset require at least 65GB of free disk space.

> **WARNING (2)**: Retriving the TUH EEG Abnormal dataset require valid credentials, you can get your own at https://www.isip.piconepress.com/projects/tuh_eeg/html/request_access.php.

In the root directory of this project there is a Makefile, by typing:

    make tuh_eeg_abnormal

you will trigger the dataset download.

## Documentation

> **WIP**: Documentation is currently Work-In-Progress, if you need additional info, please, contact me directly.

## Credits

If you use this code in your project use the citation below:

    @misc{Zanga2019PyEEGLab,
        title={PyEEGLab: a simple tool for EEG manipulation},
        author={Alessio Zanga},
        year={2019},
        howpublished={\url{https://github.com/AlessioZanga/PyEEGLab}},
    }

## Related publications

- "An Attention-based Architecture for EEG Classification" - https://www.scitepress.org/Link.aspx?doi=10.5220/0008953502140219
