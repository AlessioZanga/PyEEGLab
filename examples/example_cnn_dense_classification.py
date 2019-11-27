#!/usr/bin/env python

import warnings
warnings.simplefilter(action='ignore')

import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
tf.enable_eager_execution(config=config)

from keras.utils import to_categorical
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold
import numpy as np

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pyeeglab import TUHEEGAbnormalDataset

dataset = TUHEEGAbnormalDataset('../data', frames=8)
data, labels = dataset.load('correlations', 0.7, 25, 75, True, '../export')

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
        input_a = tf.keras.Input((*input_shape, 1))
        x = tf.keras.layers.Conv2D(8, 3)(input_a)
        x = tf.keras.layers.MaxPool2D(2)(x)
        x = tf.keras.layers.Flatten()(x)
        x = tf.keras.Model(inputs=[input_a], outputs=x)
        cnns.append(x)

    combine = tf.keras.layers.Concatenate()([x.output for x in cnns])
    z = tf.keras.layers.Dense(classes, activation='softmax')(combine)

    model = tf.keras.Model(inputs=[x.input for x in cnns], outputs=z)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train_cat, batch_size=32, epochs=50, shuffle=True, validation_split=0.1)
    y_pred = model.predict(x_test).argmax(axis=-1)
    acc = accuracy_score(y_test, y_pred)
    print("Fold accuracy: {:2.2f}".format(acc))
    matrix = confusion_matrix(y_test, y_pred)
    print("Fold confusion matrix: \n {}".format(matrix))
    total_acc += acc/n_splits

print("Total model accuracy: {:2.2f}".format(total_acc))