#!/usr/bin/env python

import warnings
warnings.simplefilter(action='ignore')

from keras.backend.tensorflow_backend import set_session
import tensorflow as tf
config = tf.ConfigProto()
config.gpu_options.allow_growth = True
sess = tf.Session(config=config)
set_session(sess)

if tf.test.is_gpu_available():
    from keras.layers import CuDNNLSTM as LSTM
else:
    from keras.layers import LSTM

from keras import Model, Input
from keras.layers import Dense, Concatenate, Reshape, Flatten, Dropout
from keras.utils import to_categorical
from sklearn.metrics import accuracy_score, confusion_matrix
from sklearn.model_selection import StratifiedKFold
from spektral.layers import GraphAttention
from spektral.utils import nx_to_adj, nx_to_node_features, add_eye
import numpy as np

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from pyeeglab import TUHEEGCorpusDataset

dataset = TUHEEGCorpusDataset('../data', frames=8)
data, labels = dataset.load('graphs', 0.7, 25, 75, True, '../export')

data = [
    [
        [
            nx_to_node_features(G, ['features'])[0],
            add_eye(nx_to_adj(G)[0])
        ]
        for G in graphs
    ]
    for graphs in data
]

data = [
    [ e for G in graphs for e in G ]
    for graphs in data
]

classes = len(set(labels))

graphs = len(data[0])
sub = int(len(data[0])/2)
F = len(data[0][0][0])
N = data[0][1].shape[0]

inputs = [[] for _ in range(graphs)]
for d in data:
    for i in range(graphs):
        inputs[i].append(d[i])
data = [np.array(i) for i in inputs]

total_acc = 0
n_splits = 10
skf = StratifiedKFold(n_splits=n_splits, shuffle=True)
for train_idx, test_idx in skf.split(data[0], labels):
    x_train, y_train = [d[train_idx] for d in data], labels[train_idx]
    x_test, y_test = [d[test_idx] for d in data], labels[test_idx]

    y_train_cat = to_categorical(y_train)
    y_test_cat = to_categorical(y_test)

    gans = []
    for _ in range(sub):
        input_a = Input((N, F))
        input_b = Input((N, N))
        x = GraphAttention(5)([input_a, input_b])
        x = Flatten()(x)
        x = Model(inputs=[input_a, input_b], outputs=x)
        gans.append(x)

    combine = Concatenate()([x.output for x in gans])
    reshape = Reshape((len(gans), gans[0].output_shape[1]))(combine)
    lstm = LSTM(32)(reshape)
    z = Dense(classes, activation='softmax')(lstm)

    model = Model(inputs=[i for x in gans for i in x.input], outputs=z)
    model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    model.fit(x_train, y_train_cat, batch_size=32, epochs=50, shuffle=True, validation_split=0.1)
    y_pred = model.predict(x_test).argmax(axis=-1)
    acc = accuracy_score(y_test, y_pred)
    print("Fold accuracy: {:2.2f}".format(acc))
    matrix = confusion_matrix(y_test, y_pred)
    print("Fold confusion matrix: \n {}".format(matrix))
    total_acc += acc/n_splits

print("Total model accuracy: {:2.2f}".format(total_acc))
