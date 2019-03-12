import os
import logging
import numpy as np
import pandas as pd
import networkx as nx
from itertools import combinations
from scipy.stats import spearmanr
from multiprocessing import Pool


class GraphGenerator():
    _logger = logging.getLogger()

    def __init__(self, freq, fps):
        self._logger.debug('Create graph generator')
        self._logger.debug('Set graph generator frequency to %s Hz', freq)
        self._frequency = freq
        self._logger.debug('Set graph generator frame per seconds to %s', fps)
        self._frames = fps

    def dataToFrames(self, data):
        step = round(self._frequency/self._frames)
        data = [data[t:t+step] for t in range(0, len(data), step)]
        return data

    def frameToCorrelation(self, frame):
        frame = spearmanr(frame)
        return frame.correlation

    def filterCorrelation(self, corr, upper, lower, approx=0.01):
        if corr >= upper*(1-approx) or corr <= lower*(1-approx):
            return 1
        return 0

    def correlationsToAdjacencies(self, data, c, p1, p2):
        rows = list(range(data[0].shape[0]))
        columns = list(range(data[0].shape[1]))
        q = [
            [
                [data[k][i][j] for k in range(len(data))]
                for j in columns
            ]
            for i in rows
        ]
        q = [
            [
                (np.percentile(q[i][j], p1), np.percentile(q[i][j], p2))
                for j in range(len(q[i]))
            ]
            for i in range(len(q))
        ]
        data = [
            [
                [
                    self.filterCorrelation(
                        data[k][i][j],
                        max(c, q[i][j][1]),
                        min(-c, q[i][j][0])
                    )
                    for j in columns
                ]
                for i in rows
            ]
            for k in range(len(data))
        ]
        return data

    def matrixToList(self, adj, comb):
        adj = [adj[y][x] > 0 for (x, y) in comb]
        return adj

    def adjacencyToGraph(self, adj):
        nodes = adj.index.to_list()
        adj = adj[adj > 0].stack().index.to_list()
        adj = list(filter(lambda x: x[0] != x[1], adj))
        G = nx.Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(adj)
        return G

    def dataframeToGraphs(self, data, c, p1, p2, adj_only=False):
        index = data.columns
        data = self.dataToFrames(data)
        data = [self.frameToCorrelation(frame) for frame in data]
        data = self.correlationsToAdjacencies(data, c, p1, p2)
        data = [pd.DataFrame(d, index=index, columns=index) for d in data]
        if adj_only:
            comb = list(combinations(index, 2))
            data = [self.matrixToList(adj, comb) for adj in data]
        else:
            data = [self.adjacencyToGraph(adj) for adj in data]
        return data

    def dataframesToGraphs(self, data, c, p1, p2, adj_only=False):
        self._logger.debug('Load dataset to generate graphs')
        self._logger.debug('Create process pool')
        pool = Pool(len(os.sched_getaffinity(0)))
        self._logger.debug('Start process pool')
        data = list(zip(
            data,
            [c] * len(data),
            [p1] * len(data),
            [p2] * len(data),
            [adj_only] * len(data)
        ))
        data = pool.starmap(self.dataframeToGraphs, data)
        pool.close()
        pool.join()
        self._logger.debug('End process pool')
        return data
