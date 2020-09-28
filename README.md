# PyEEGLab

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.3874461.svg)](https://doi.org/10.5281/zenodo.3874461) [![Project Status: WIP – Initial development is in progress, but there has not yet been a stable, usable release suitable for the public.](https://www.repostatus.org/badges/latest/wip.svg)](https://www.repostatus.org/#wip) [![Build Status](https://travis-ci.org/AlessioZanga/PyEEGLab.svg?branch=master)](https://travis-ci.org/AlessioZanga/PyEEGLab) [![Documentation Status](https://readthedocs.org/projects/pyeeglab/badge/?version=latest)](https://pyeeglab.readthedocs.io/en/latest/?badge=latest) [![codecov](https://codecov.io/gh/AlessioZanga/PyEEGLab/branch/master/graph/badge.svg)](https://codecov.io/gh/AlessioZanga/PyEEGLab) [![Maintainability](https://api.codeclimate.com/v1/badges/c55f67ee28e9e8bd8038/maintainability)](https://codeclimate.com/github/AlessioZanga/PyEEGLab/maintainability) [![CodeFactor](https://www.codefactor.io/repository/github/alessiozanga/pyeeglab/badge)](https://www.codefactor.io/repository/github/alessiozanga/pyeeglab) [![Gitpod Ready-to-Code](https://img.shields.io/badge/Gitpod-Ready--to--Code-blue?logo=gitpod)](https://gitpod.io/#https://github.com/AlessioZanga/PyEEGLab) 

Analyze and manipulate EEG data using PyEEGLab.

## Introduction

PyEEGLab is a python package developed to define pipeline for EEG preprocessing for a wide range of machine learning tasks. It supports set of datasets out-of-the-box and allow you to adapt your preferred one.

## How it Works

Here is a simple quickstart:

    from pyeeglab import *
    dataset = TUHEEGAbnormalDataset()
    preprocessing = Pipeline([
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

If you need a bleeding edge version, you can install it directly from GitHub:

    pip install git+https://github.com/AlessioZanga/PyEEGLab@develop

## Out-Of-The-Box Supported Datasets

The following datasets will work upon downloading:

| Dataset | Size&nbsp;(GB) | Class&nbsp;Distribution | Task | Notes |
|---------|---------------:|:------------------------|------|-------|
| [TUH Abnormal EEG Dataset](https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml) | 59.0 GB | 'normal': 1521 <br /> 'abnormal': 1472 | Generic abnormal EEG events vs. normal EEG traces. | This dataset does not contain any annotation, the event extraction is performed according to other papers that used this dataset: for each record a 60s sample is extracted and labelled according to the class of the file. |
| [TUH Artifact EEG Dataset](https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml) | 5.5 GB  | 'null': 1940 <br /> 'eyem': 606 <br /> 'musc': 254 <br /> 'elpp': 178 <br /> 'chew': 161 <br /> 'shiv': 60 | Multiple artifacts vs. EEG baseline. | At the moment, only the '01_tcp_ar' EEG reference setup can be used (more than ~95% of total records). |
| [TUH Seizure EEG Dataset](https://www.isip.piconepress.com/projects/tuh_eeg/html/downloads.shtml) | 54.0 GB | 'fnsz': 4240 <br /> 'gnsz': 1717 <br /> 'cpsz': 1496 <br /> 'tnsz': 334 <br /> 'tcsz': 191 <br /> 'mysz': 6 <br /> 'absz': 2 | Generic unclassified seizure type vs. specific seizure types. | At the moment, only the '01_tcp_ar' EEG reference setup can be used (more than ~95% of total records). <br /> Also, 'bckg' and 'scpz' classes are ignored: the former is just (a lot of) background noise, the latter has just one instance, which cannot be used with stratified cross-validation. |
| [Motor Movement/Imagery EEG Dataset](https://physionet.org/content/eegmmidb/1.0.0/) | 3.4 GB | | Motor movement / imagery events. | The size of this dataset will increase a lot during preprocessing: although its download size is fairly small, the records of this dataset are entirely annotated, meaning that the whole dataset is suitable for feature extraction, not just sparse events like the others datasets. |
| [CHB-MIT Scalp EEG Dataset](https://physionet.org/content/chbmit/1.0.0/) | 43.0 GB | 'noseizure': 545 <br /> 'seizure': 184 | No seizure events vs. seizure events. | While for 'seizure' events there are (begin, end, label) records, the 'noseizure' class is computed by extracting a 60s sample from records that are flagged as 'noseizure'. |

## How to Class Meaning - From the TUH Seizure docs

<div style="font-size: 85%;">

| **Class&nbsp;Code** | **Event&nbsp;Name**                               | **Description**                                                                                                    |
| -------------- | -------------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| _NULL_         | No Event                                     | An unclassified event                                                                                              |
| _SPSW_         | Spike/Sharp and Wave                         | Spike and wave/complexes , sharp and wave/complexes                                                                |
| _GPED_         | Generalized Periodic Epileptiform Discharges | Diffused periodic discharges                                                                                       |
| _PLED_         | Periodic Lateralized Epileptiform Discharges | Focal periodic discharges                                                                                          |
| _EYBL_         | Eye blink                                    | A specific type of sharp, high amplitude eye movement artifact corresponding to blinks                             |
| _ARTF_         | Artifacts (All)                              | Any non-brain activity electrical signal, such as those due to equipment or environmental factors                  |
| _BCKG_         | Background                                   | Baseline/non-interesting events                                                                                    |
| _SEIZ_         | Seizure                                      | Common seizure class which can include all types of seizure                                                        |
| _FNSZ_         | Focal Non-Specific Seizure                   | Focal seizures which cannot be specified with its type                                                             |
| _GNSZ_         | Generalized Non-Specific Seizure             | Generalized seizures which cannot be further classified into one of the groups below                               |
| _SPSZ_         | Simple Partial Seizure                       | Partial seizures during consciousness; Type specified by clinical signs only                                       |
| _CPSZ_         | Complex Partial Seizure                      | Partial Seizures during unconsciousness; Type specified by clinical signs only                                     |
| _ABSZ_         | Absence Seizure                              | Absence Discharges observed on EEG; patient loses consciousness for few seconds (Petit Mal)                        |
| _TNSZ_         | Tonic Seizure                                | Stiffening of body during seizure (EEG effects disappears)                                                         |
| _CNSZ_         | Clonic Seizure                               | Jerking/shivering of body during seizure                                                                           |
| _TCSZ_         | Tonic Clonic Seizure                         | At first stiffening and then jerking of body (Grand Mal)                                                           |
| _ATSZ_         | Atonic Seizure                               | Sudden loss of muscle tone                                                                                         |
| _MYSZ_         | Myoclonic Seizure                            | Myoclonous jerks of limbs                                                                                          |
| _NESZ_         | Non-Epileptic Seizure                        | Any non-epileptic seizure observed. Contains no electrographic signs.                                              |
| _INTR_         | Interesting Patterns                         | Any unusual or interesting patterns observed that don't fit into the above classes.                                |
| _SLOW_         | Slowing                                      | A brief decrease in frequency                                                                                      |
| _EYEM_         | Eye Movement Artifact                        | A very common frontal/prefrontal artifact seen when the eyes move                                                  |
| _CHEW_         | Chewing Artifact                             | A specific artifact involving multiple channels that corresponds with patient chewing, “bursty”                    |
| _SHIV_         | Shivering Artifact                           | A specific, sustained sharp artifact that corresponds with patient shivering.                                      |
| _MUSC_         | Muscle Artifact                              | A very common, high frequency, sharp artifact that corresponds with agitation/nervousness in a patient.            |
| _ELPP_         | Electrode Pop Artifact                       | A short artifact characterized by channels using the same electrode “spiking” with perfect symmetry.               |
| _ELST_         | Electrostatic Artifact                       | Artifact caused by movement or interference on the electrodes, variety of morphologies.                            |
| _CALB_         | Calibration Artifact                         | Artifact caused by calibration of the electrodes. Appears as a flattening of the signal in the beginning of files. |
| _HPHS_         | Hypnagogic Hypersynchrony                    | A brief period of high amplitude slow waves.                                                                       |
| _TRIP_         | Triphasic Wave                               | Large, three-phase waves frequently caused by an underlying metabolic condition.                                   |
| _ELEC_         | Electrode Artifact                           | Electrode pop, Electrostatic artifacts, Lead artifacts.                                                            |

</div>

## How to Get a Dataset

> **WARNING**: Retriving the TUH EEG datasets require valid credentials, you can get your own at: https://www.isip.piconepress.com/projects/tuh_eeg/html/request_access.php.

Given the dataset instance, trigger the download using the "download" method:

    from pyeeglab import *
    dataset = TUHEEGAbnormalDataset()
    dataset.download(user='USER', password='PASSWORD')
    dataset.index()

then index the new downloaded files.

It should be noted that the download mechanism work on Unix-like systems given the following packages:

    sudo apt install sshpass rsync wget

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
