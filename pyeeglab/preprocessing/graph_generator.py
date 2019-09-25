import logging
from typing import List
from itertools import combinations
from yasa import bandpower
from numpy import percentile
from pandas import DataFrame
from scipy.stats import spearmanr
from networkx import Graph, set_node_attributes


class GraphGenerator():

    def __init__(self, frequency: float, frames: int) -> None:
        logging.debug('Create graph generator')
        logging.debug('Set graph generator frequency to %s Hz', frequency)
        self.frequency = frequency
        logging.debug('Set graph generator frame per seconds to %s', frames)
        self.frames = frames

    def data_to_frames(self, data: DataFrame) -> List[DataFrame]:
        step = len(data)
        if self.frames > 1:
            step = round(step/self.frames)
        return [data[t:t+step] for t in range(0, len(data), step)]

    def extract_features(self, frame: DataFrame, bands: List[str] = ['Delta', 'Theta', 'Alpha', 'Beta', 'Gamma']) -> DataFrame:
        frame = frame.swapaxes('index', 'columns')
        bandp = bandpower(frame.to_numpy(), self.frequency, frame.index)
        return bandp.loc[:, bands]

    def frame_to_correlation(self, frame: DataFrame) -> DataFrame:
        index = frame.columns
        frame = spearmanr(frame)
        return DataFrame(frame.correlation, index=index, columns=index)

    def filter_correlation(self, corr: float, upper: float, lower: float, approx=0.01) -> bool:
        if corr >= upper*(1-approx) or corr <= lower*(1-approx):
            return True
        return False

    def correlations_to_adjacencies(self, data: List[DataFrame], c: float, p1: int, p2: int) -> List[DataFrame]:
        index = data[0].index
        samples = list(range(len(data)))
        rows = list(range(data[0].shape[0]))
        columns = list(range(data[0].shape[1]))
        q = [
            [
                [data[k].iloc[i, j] for k in samples]
                for j in columns
            ]
            for i in rows
        ]
        q = [
            [
                (percentile(q[i][j], p1), percentile(q[i][j], p2))
                for j in columns
            ]
            for i in rows
        ]
        data = [
            [
                [
                    self.filter_correlation(
                        data[k].iloc[i, j],
                        max(+c, q[i][j][1]),
                        min(-c, q[i][j][0])
                    )
                    for j in columns
                ]
                for i in rows
            ]
            for k in samples
        ]
        data = [DataFrame(d, index=index, columns=index) for d in data]
        return data

    def matrix_to_list(self, adj: DataFrame) -> List[float]:
        com = list(combinations(sorted(adj.index), 2))
        adj = [adj[y][x] for (x, y) in com]
        return adj

    def adjacency_to_graph(self, adj: DataFrame, features: DataFrame = None) -> Graph:
        nodes = sorted(adj.index)
        adj = adj[adj > 0].stack().index.to_list()
        adj = [x for x in adj if x[0] != x[1]]
        G = Graph()
        G.add_nodes_from(nodes)
        G.add_edges_from(adj)
        if features is not None:
            features = {node: {'features': features.loc[node, : ].to_numpy()} for node in nodes}
            set_node_attributes(G, features)
        return G

    def dataframe_to_graphs(self, data: DataFrame, c: float, p1: int, p2: int, adj_only=False, weighted=False, node_features=False):
        data = self.data_to_frames(data)
        if node_features:
            features = [self.extract_features(frame) for frame in data]
        data = [self.frame_to_correlation(frame) for frame in data]
        if not weighted:
            data = self.correlations_to_adjacencies(data, c, p1, p2)
        if adj_only:
            data = [self.matrix_to_list(adj) for adj in data]
        else:
            if not node_features:
                data = [self.adjacency_to_graph(frame) for frame in data]
            else:
                data = [self.adjacency_to_graph(data[i], features[i]) for i in range(len(data))]
        return data
