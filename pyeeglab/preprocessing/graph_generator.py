import logging
from typing import List
from itertools import combinations
from scipy.stats import spearmanr
from yasa import bandpower
from pandas import DataFrame
import numpy as np
import networkx as nx


class GraphGenerator():
    _logger = logging.getLogger()

    def __init__(self, freq: float, fps: int) -> None:
        self._logger.debug('Create graph generator')
        self._logger.debug('Set graph generator frequency to %s Hz', freq)
        self._frequency = freq
        self._logger.debug('Set graph generator frame per seconds to %s', fps)
        self._frames = fps

    def data_to_frames(self, data: DataFrame) -> List[DataFrame]:
        step = len(data)
        if self._frames >= 1:
            step = round(step/self._frames)
        data = [data[t:t+step] for t in range(0, len(data), step)]
        return data
    
    def extract_features(self, frame: DataFrame, bands=['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']) -> DataFrame:
        frame = frame.swapaxes('index', 'columns')
        bandp = bandpower(frame.to_numpy() , self._frequency, frame.index)
        return bandp.loc[ : , bands]

    def frame_to_correlation(self, frame: DataFrame) -> DataFrame:
        frame = spearmanr(frame)
        return frame.correlation

    def filter_correlation(self, corr: float, upper: float, lower: float, approx=0.01) -> bool:
        if corr >= upper*(1-approx) or corr <= lower*(1-approx):
            return True
        return False

    def correlations_to_adjacencies(self, data: List[DataFrame], c: int, p1: float, p2: float) -> List[DataFrame]:
        samples = list(range(len(data)))
        rows = list(range(data[0].shape[0]))
        columns = list(range(data[0].shape[1]))
        q = [
            [
                [data[k][i][j] for k in samples]
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
                    self.filter_correlation(
                        data[k][i][j],
                        max(c, q[i][j][1]),
                        min(-c, q[i][j][0])
                    )
                    for j in columns
                ]
                for i in rows
            ]
            for k in samples
        ]
        return data

    def matrix_to_list(self, adj: DataFrame) -> List[float]:
        com = list(combinations(sorted(adj.index), 2))
        adj = [adj[y][x] for (x, y) in com]
        return adj

    def adjacency_to_graph(self, adj: DataFrame, node_features: DataFrame):
        nodes = sorted(adj.index)
        adj = adj[adj > 0].stack().index.to_list()
        adj = [x for x in adj if x[0] != x[1]]
        g = nx.Graph()
        g.add_nodes_from(nodes)
        g.add_edges_from(adj)
        if node_features is not None:
            features = {node: {'features': node_features.loc[node, : ].to_numpy()} for node in nodes}
            nx.set_node_attributes(g, features)
        return g

    def dataframe_to_graphs(self, data: DataFrame, c: int, p1: float, p2: float, adj_only=False, weighted=False, node_features=False):
        index = data.columns
        data = self.data_to_frames(data)
        if node_features:
            features = [self.extract_features(frame) for frame in data]
        data = [self.frame_to_correlation(frame) for frame in data]
        if not weighted:
            data = self.correlations_to_adjacencies(data, c, p1, p2)
        data = [DataFrame(d, index=index, columns=index) for d in data]
        if adj_only:
            data = [self.matrix_to_list(adj) for adj in data]
        else:
            if not node_features:
                data = [self.adjacency_to_graph(frame) for frame in data]
            else:
                data = [self.adjacency_to_graph(data[i], features[i]) for i in range(len(data))]
        return data
