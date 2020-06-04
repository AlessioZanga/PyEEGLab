import logging
import json

import pandas as pd
import networkx as nx
from networkx.convert_matrix import from_pandas_edgelist

from ...pipeline import Preprocessor

from typing import List


class GraphGenerator(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create new graph generator preprocessor')

    def run(self, data: List[pd.DataFrame], **kwargs) -> List[nx.Graph]:
        nodes = [set(d.From.to_list() + d.To.to_list()) for d in data]
        edges = [d.where(d.Weight != 0).dropna().reset_index(drop=True) for d in data]
        graphs = []
        for i in range(len(data)):
            graph = from_pandas_edgelist(edges[i], 'From', 'To')
            graph.add_nodes_from(nodes[i])
            graphs.append(graph)
        return graphs


class GraphWithFeatures(GraphGenerator):

    def __init__(self):
        super().__init__()
        logging.debug('Create new graph with features preprocessor')

    def _run(self, adjacency: List[pd.DataFrame], features: List[pd.DataFrame], **kwargs) -> List[nx.Graph]:
        graphs = super().run(adjacency, **kwargs)
        for i, graph in enumerate(graphs):
            feature = {
                node: {'features': features[i].loc[node, :].to_numpy()}
                for node in graph.nodes
            }
            nx.set_node_attributes(graph, feature)
        return graphs

    def run(self, data, **kwargs) -> List[nx.Graph]:
        return self._run(*data, **kwargs)
