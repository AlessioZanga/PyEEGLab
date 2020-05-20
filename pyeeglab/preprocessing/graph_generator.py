import logging
from typing import List

from json import dumps
from pandas import DataFrame
from networkx import Graph, set_node_attributes
from networkx.convert_matrix import from_pandas_edgelist

from .pipeline import Preprocessor


class GraphGenerator(Preprocessor):

    def __init__(self) -> None:
        super().__init__()
        logging.debug('Create new graph generator preprocessor')

    def run(self, data: List[DataFrame], **kwargs) -> List[Graph]:
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

    def _run(self, adjacency: List[DataFrame], features: List[DataFrame], **kwargs) -> List[Graph]:
        graphs = super().run(adjacency, **kwargs)
        for i, graph in enumerate(graphs):
            feature = {
                node: {'features': features[i].loc[node, :].to_numpy()}
                for node in graph.nodes
            }
            set_node_attributes(graph, feature)
        return graphs

    def run(self, data, **kwargs) -> List[Graph]:
        return self._run(*data, **kwargs)
