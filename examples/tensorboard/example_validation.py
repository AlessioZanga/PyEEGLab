#!/usr/bin/env python

# Ignore MNE and TensorFlow warnings
import warnings
warnings.simplefilter(action='ignore')

# Import TensorFlow with GPU memory settings
import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
try:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
except RuntimeError as e:
    print(e)

# Import TensorBoard params and metrics
from tensorboard.plugins.hparams import api as hp
from tensorflow.keras.metrics import Accuracy, Precision, Recall

# Import Spektral for GraphAttention
import spektral as sp

# Others imports
import os
import pickle
import numpy as np
import pandas as pd
from random import shuffle
from itertools import product
from sklearn.model_selection import train_test_split, StratifiedKFold
from tensorflow.python.keras.utils.np_utils import to_categorical

# Relative import PyEEGLab
import sys
from os.path import abspath, dirname, join

sys.path.insert(0, abspath(join(dirname(__file__), '../..')))
from pyeeglab import *

def build_data(dataset):
    dataset.set_cache_manager(PickleCache('../../export'))

    preprocessing = Pipeline([
        CommonChannelSet(),
        LowestFrequency(),
        ToDataframe(),
        MinMaxCentralizedNormalization(),
        DynamicWindow(8),
        ForkedPreprocessor(
            inputs=[
                SpearmanCorrelation(),
                Mean(),
                Variance(),
                Skewness(),
                Kurtosis(),
                ZeroCrossing(),
                AbsoluteArea(),
                PeakToPeak(),
                Bandpower(['Delta', 'Theta', 'Alpha', 'Beta'])
            ],
            output=ToMergedDataframes()
        ),
        ToNumpy()
    ])

    return dataset.set_pipeline(preprocessing).load()

def adapt_data(data, test_size=0.1):
    if isinstance(data, str):
        with open(data, 'rb') as f:
            data = pickle.load(f)
    samples, labels = data['data'], data['labels']
    x_train, x_test, y_train, y_test = train_test_split(samples, labels, test_size=test_size, shuffle=True, stratify=labels)
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=test_size, shuffle=True, stratify=y_train)
    classes = np.sort(np.unique(labels))
    y_train = to_categorical(y_train, num_classes=len(classes))
    y_test = to_categorical(y_test, num_classes=len(classes))
    y_val = to_categorical(y_val, num_classes=len(classes))
    return x_train, y_train, x_val, y_val, x_test, y_test

def stratified_k_cross_validation_split(data, folds):
    if isinstance(data, str):
        with open(data, 'rb') as f:
            data = pickle.load(f)
    samples, labels = data['data'], data['labels']
    skf = StratifiedKFold(n_splits=folds, shuffle=True)
    return samples, labels, skf.split(samples, labels)

def build_model(shape, classes, hparams, metrics):
    print(hparams)
    N = shape[2]
    F = shape[3] - N
    frames = shape[1]

    def get_frame(x, frame, N, F):
        x = tf.slice(x, [0, frame, 0, 0], [-1, 1, N, F])
        x = tf.squeeze(x, axis=[1])
        return x

    input_0 = tf.keras.Input((frames, N, F + N))

    layers = []
    for frame in range(frames):
        frame_matrix = tf.keras.layers.Lambda(
            get_frame,
            arguments={'frame': frame, 'N': N, 'F': F}
        )(input_0)
        
        x = tf.keras.layers.Conv1D(hparams['filters'], hparams['kernel'], data_format='channels_first')(frame_matrix)
        x = tf.keras.layers.MaxPooling1D(hparams['pool'])(x)
        x = tf.keras.layers.Flatten()(x)
        layers.append(x)

    combine = tf.keras.layers.Concatenate()(layers)
    reshape = tf.keras.layers.Reshape((-1, frames))(combine)
    lstm = tf.keras.layers.LSTM(hparams['hidden_units'])(reshape)
    dropout = tf.keras.layers.Dropout(hparams['dropout'])(lstm)
    out = tf.keras.layers.Dense(classes, activation='softmax')(dropout)

    model = tf.keras.Model(inputs=[input_0], outputs=out)
    model.compile(
        optimizer=tf.keras.optimizers.Adam(learning_rate=hparams['learning_rate']),
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            Recall(class_id=0, name='recall'),
            Specificity(class_id=0, name='specificity'),
            Precision(class_id=0, name='precision'),
            F1Score(class_id=0, name='f1score'),
        ]
    )
    model.summary()
    model.save('logs/plot_cnn.h5')
    return model

def run_trial(path, step, model, hparams, metrics, x_train, y_train, x_test, y_test, epochs):
    with tf.summary.create_file_writer(path).as_default():
        hp.hparams(hparams)
        model.fit(x_train, y_train, epochs=epochs, batch_size=32, shuffle=True)
        metrics_output = model.evaluate(x_test, y_test)
        metrics_output = dict(zip(model.metrics_names, metrics_output))
        for metric_name, metric_value in metrics_output.items():
            if metric_name in metrics:
                tf.summary.scalar(metric_name, metric_value, step=step)
        return metrics_output

def hparams_combinations(hparams, metrics):
    hp.hparams_config(
        hparams=list(hparams.values()),
        metrics=[
            hp.Metric(metric, display_name=metric.capitalize())
            for metric in metrics
        ]
    )
    hparams_keys = list(hparams.keys())
    hparams_values = list(product(*[
        h.domain.values
        for h in hparams.values()
    ]))
    hparams = [
        dict(zip(hparams_keys, values))
        for values in hparams_values
    ]
    shuffle(hparams)
    return hparams

def tune_model(dataset_name, data, metrics, folds, val_size=0.1):
    LOGS_DIR = join('./logs/cnn', dataset_name)
    os.makedirs(LOGS_DIR, exist_ok=True)
    # Prepare the data
    data, labels, splitter = stratified_k_cross_validation_split(data, folds)
    # Set tuning session and results
    counter = 0
    results = []
    # Parameters to be tuned
    hparam = {
        'learning_rate': 1e-4,
        'kernel': 5,
        'filters': 32,
        'pool': 5,
        'hidden_units': 64,
        'dropout': 0.10,
    }
    for train_idx, test_idx in splitter:
        # Generate folds
        x_train, y_train = data[train_idx], labels[train_idx]
        x_test, y_test = data[test_idx], labels[test_idx]
        classes = np.sort(np.unique(labels))
        y_train = to_categorical(y_train, num_classes=len(classes))
        y_test = to_categorical(y_test, num_classes=len(classes))
        # Build the model
        model = build_model(data.shape, len(classes), hparam, metrics)
        # Run session
        run_name = f'run-{counter}'
        print(f'--- Starting trial: {run_name}')
        print(hparam)
        result = run_trial(
            join(LOGS_DIR, run_name),
            counter,
            model,
            hparam,
            metrics,
            x_train,
            y_train,
            x_test,
            y_test,
            epochs=50
        )
        counter += 1
        results.append(result)
    results = pd.DataFrame(results)
    hparam = '-'.join([
        str(key) + '_' + str(value)
        for key, value in hparam.items()
    ])
    results.to_csv(join(LOGS_DIR, "validation-{}-{}-results.csv".format(dataset_name, hparam)))
    print(results)


if __name__ == '__main__':
    dataset = {}
    
    # dataset['tuh_eeg_abnormal'] = TUHEEGAbnormalDataset('../../data/tuh_eeg_abnormal/v2.0.0/edf')

    # dataset['tuh_eeg_artifact'] = TUHEEGArtifactDataset('../../data/tuh_eeg_artifact/v1.0.0/edf')
    # dataset['tuh_eeg_artifact'].set_minimum_event_duration(4)

    # dataset['tuh_eeg_seizure'] = TUHEEGSeizureDataset('../../data/tuh_eeg_seizure/v1.5.2/edf')
    # dataset['tuh_eeg_seizure'].set_minimum_event_duration(4)

    # dataset['eegmmidb'] = EEGMMIDBDataset('../../data/physionet.org/files/eegmmidb/1.0.0')
    # dataset['eegmmidb'].set_minimum_event_duration(4)

    dataset['chbmit'] = CHBMITDataset('../../data/physionet.org/files/chbmit/1.0.0')
    dataset['chbmit'].set_minimum_event_duration(4)

    """
        Note: You can just use paths as values in the dictionary
        and comment-out the first line of the following for cycle ;)
    """

    for key, value in dataset.items():
        metrics = [
            'accuracy', 
            'recall',
            'specificity',
            'precision',
            'f1score',
        ]
        value = build_data(value)
        tune_model(key, value, metrics, folds=10)
