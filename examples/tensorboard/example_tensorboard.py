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
from tensorflow.keras.metrics import Precision, Recall

# Import Spektral for GraphAttention
import spektral as sp

# Others imports
import os
import numpy as np
from random import shuffle
from itertools import product
from networkx import to_numpy_matrix
from sklearn.model_selection import train_test_split
from tensorflow.python.keras.utils.np_utils import to_categorical

# Relative import PyEEGLab
import sys
from os.path import abspath, dirname, join

sys.path.insert(0, abspath(join(dirname(__file__), '../..')))
from pyeeglab import *

# Parameters to be tuned
HP_HIDDEN_UNITS = hp.HParam('hidden_units', hp.Discrete([32, 64, 128, 256]))
HP_OUTPUT_SHAPE = hp.HParam('output_shape', hp.Discrete([8, 16, 32, 64]))

def build_data():
    dataset = TUHEEGAbnormalDataset('../../data/tuh_eeg_abnormal/v2.0.0/edf')
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

def adapt_data(data, test_size=0.1, shuffle=True):
    samples, labels = data['data'], data['labels']
    x_train, x_test, y_train, y_test = train_test_split(samples, labels, test_size=test_size, shuffle=shuffle, stratify=labels)
    x_train, x_val, y_train, y_val = train_test_split(x_train, y_train, test_size=test_size, shuffle=shuffle, stratify=y_train)
    classes = np.sort(np.unique(labels))
    y_train = to_categorical(y_train, num_classes=len(classes))
    y_test = to_categorical(y_test, num_classes=len(classes))
    y_val = to_categorical(y_val, num_classes=len(classes))
    return x_train, y_train, x_val, y_val, x_test, y_test

def build_model(shape, classes, hparams):
    N = shape[2]
    F = shape[3]
    frames = shape[1]

    def get_feature_matrix(x, frame, N, F):
        return tf.slice(x, [0, frame, 0, N], [-1, 1, N, (F-N)])
    
    def get_correlation_matrix(x, frame, N, F):
        return tf.slice(x, [0, frame, 0, 0], [-1, 1, N, N])

    input_0 = tf.keras.Input((frames, N, F))

    gans = []
    for frame in range(frames):
        feature_matrix = tf.keras.layers.Lambda(
            get_feature_matrix,
            arguments={'frame': frame, 'N': N, 'F': F}
        )(input_0)

        correlation_matrix = tf.keras.layers.Lambda(
            get_correlation_matrix,
            arguments={'frame': frame, 'N': N, 'F': F}
        )(input_0)
        
        x = sp.layers.GraphAttention(hparams['HP_OUTPUT_SHAPE'])([feature_matrix, correlation_matrix])
        x = tf.keras.layers.Flatten()(x)
        gans.append(x)

    combine = tf.keras.layers.Concatenate()(gans)
    reshape = tf.keras.layers.Reshape((frames, N * hparams['HP_OUTPUT_SHAPE']))(combine)
    lstm = tf.keras.layers.LSTM(hparams['HP_HIDDEN_UNITS'])(reshape)
    out = tf.keras.layers.Dense(classes, activation='softmax')(lstm)

    model = tf.keras.Model(inputs=[input_0], outputs=out)
    model.compile(
        optimizer='adam',
        loss='categorical_crossentropy',
        metrics=[
            'accuracy',
            Recall(class_id=0, name='recall'),
            Precision(class_id=0, name='precision'),
        ]
    )
    model.summary()
    return model

def run_trial(path, model, hparams, x_train, y_train, x_val, y_val, x_test, y_test, epochs):
    hp.hparams(hparams)
    model.fit(x_train, y_train, epochs=epochs, batch_size=32, shuffle=True, validation_data=(x_val, y_val))
    loss, accuracy, recall, precision = model.evaluate(x_test, y_test)
    tf.summary.scalar('accuracy', accuracy, step=1)
    tf.summary.scalar('recall', recall, step=1)
    tf.summary.scalar('precision', precision, step=1)

def hparams_comb():
    hp.hparams_config(
        hparams=[
            HP_HIDDEN_UNITS,
            HP_OUTPUT_SHAPE,
        ],
        metrics=[
            hp.Metric('accuracy', display_name='Accuracy'),
            hp.Metric('recall', display_name='Recall'),
            hp.Metric('precision', display_name='Precision'),
        ]
    )
    hparams_combinations = list(product(
        HP_HIDDEN_UNITS.domain.values,
        HP_OUTPUT_SHAPE.domain.values,
    ))
    shuffle(hparams_combinations)
    return hparams_combinations

def tune_model(data):
    LOGS_DIR = './tensorboard'
    os.makedirs(LOGS_DIR, exist_ok=True)
    # Prepare the data
    x_train, y_train, x_val, y_val, x_test, y_test = adapt_data(data)
    # Set tuning session
    with tf.summary.create_file_writer(LOGS_DIR).as_default():
        hparams_combinations = hparams_comb()
        counter = 0
        for params_config in hparams_combinations:
            hparams = {
                'HP_HIDDEN_UNITS': params_config[0],
                'HP_OUTPUT_SHAPE': params_config[1],
            }
            # Build the model
            model = build_model(data['data'].shape, len(data['labels_encoder']), hparams)
            # Run session
            run_name = f'run-{counter}'
            print(f'--- Starting trial: {run_name}')
            print(hparams)
            run_trial(
                join(LOGS_DIR, run_name),
                model,
                hparams,
                x_train,
                y_train,
                x_val,
                y_val,
                x_test,
                y_test,
                epochs=50
            )
            counter += 1


if __name__ == '__main__':
    data = build_data()
    tune_model(data)
