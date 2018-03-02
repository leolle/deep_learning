# -*- coding: utf-8 -*-
import networkx as nx
import random
import uuid
import copy

depth = 2
graph = nx.DiGraph()
root_node = [1]
base_nodes = []
end_nodes = []
i = 0
for _ in range(random.randint(1, 3)):
    base_nodes.append(str(uuid.uuid4()))
while i < depth:
    # for _ in range(random.randint(1, 5)):
    #     base_nodes.append(str(uuid.uuid4()))
    for index, b in enumerate(base_nodes):
        nodes = [str(uuid.uuid4()) for _ in range(random.randint(2, 3))]
        end_nodes.extend(nodes)
        for n in nodes:
            graph.add_edge(b, n)
    base_nodes = copy.copy(end_nodes)
    end_nodes = []
    i += 1
nx.write_gexf(graph, "random.gexf")
