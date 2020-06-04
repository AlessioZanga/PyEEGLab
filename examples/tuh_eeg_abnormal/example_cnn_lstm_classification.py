#!/usr/bin/env python
import warnings
warnings.simplefilter(action='ignore')

import tensorflow as tf
gpus = tf.config.experimental.list_physical_devices('GPU')
try:
    for gpu in gpus:
        tf.config.experimental.set_memory_growth(gpu, True)
except RuntimeError as e:
    print(e)

from tensorflow.keras import Model, Input
from tensorflow.keras.layers import Dense, Concatenate, Reshape, Flatten, Conv2D, MaxPool2D, LSTM
from tensorflow.keras.utils import to_categorical
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold
import numpy as np

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from pyeeglab import    TUHEEGAbnormalDataset, PickleCache, Pipeline, CommonChannelSet, \
                        LowestFrequency, ToDataframe, DynamicWindow, BinarizedSpearmanCorrelation, \
                        ToNumpy

dataset = TUHEEGAbnormalDataset('../../data/tuh_eeg_abnormal/v2.0.0/edf')
dataset.set_cache_manager(PickleCache('../../export'))

preprocessing = Pipeline([
    CommonChannelSet(),
    LowestFrequency(),
    ToDataframe(),
    DynamicWindow(8),
    BinarizedSpearmanCorrelation(),
    ToNumpy()
])

dataset = dataset.set_pipeline(preprocessing).load()
data, labels = dataset['data'], dataset['labels']

adjs = data[0].shape[0]
classes = len(set(labels))
input_shape = data[0].shape[1:]

inputs = [[] for _ in range(adjs)]
for d in data:
    for i in range(adjs):
        inputs[i].append(d[i].reshape((*input_shape, 1)))
data = [np.array(i) for i in inputs]

total_acc = 0
n_splits = 10
skf = StratifiedKFold(n_splits=n_splits, shuffle=True)
for train_idx, test_idx in skf.split(data[0], labels):
    x_train, y_train = [d[train_idx] for d in data], labels[train_idx]
    x_test, y_test = [d[test_idx] for d in data], labels[test_idx]

    y_train_cat = to_categorical(y_train)
    y_test_cat = to_categorical(y_test)

    cnns = []
    for _ in range(adjs):
        input_a = Input((*input_shape, 1))
        x = Conv2D(8, 3)(input_a)
        x = MaxPool2D(2)(x)
        x = Flatten()(x)
        x = Model(inputs=[input_a], outputs=x)
        cnns.append(x)

    combine = Concatenate()([x.output for x in cnns])
    reshape = Reshape((len(cnns), cnns[0].output_shape[1]))(combine)
    lstm = LSTM(32)(reshape)
    z = Dense(classes, activation='softmax')(lstm)

    model = Model(inputs=[x.input for x in cnns], outputs=z)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train_cat, batch_size=32, epochs=50, shuffle=True, validation_split=0.1)
    y_pred = model.predict(x_test).argmax(axis=-1)
    acc = accuracy_score(y_test, y_pred)
    print("Fold accuracy: {:2.2f}".format(acc))
    matrix = confusion_matrix(y_test, y_pred)
    print("Fold confusion matrix: \n {}".format(matrix))
    total_acc += acc/n_splits

print("Total model accuracy: {:2.2f}".format(total_acc))