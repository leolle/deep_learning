# -*- coding: utf-8 -*-
import networkx as nx
import matplotlib.pyplot as plt

G = nx.Graph()

# G.add_node(1)
# G.add_nodes_from([2, 3])
# H = nx.path_graph(10)
# G.add_nodes_from(H)
# G.add_node(H)
# G.add_edge(1, 2)
# e = (2, 3)
# G.add_edge(*e)  # unpack edge tuple*
# G.add_edges_from([(1, 2), (1, 3)])
# G.add_edges_from([(1, 2), (1, 3)])
# G.add_node(1)
# G.add_edge(1, 2)
# G.add_node("spam")  # adds node "spam"
# G.add_nodes_from("spam")  # adds 4 nodes: 's', 'p', 'a', 'm'
# G.add_edge(3, 'm')
# G.number_of_nodes()

# print(G.number_of_edges())

# G = nx.petersen_graph()
# plt.subplot(121)
# nx.draw(G, with_labels=True, font_weight='bold')
# plt.subplot(122)
# nx.draw_shell(
#     G, nlist=[range(5, 10), range(5)], with_labels=True, font_weight='bold')
# # plt.show()

# DG = nx.DiGraph()
# DG.add_weighted_edges_from([(1, 2, 0.5), (3, 1, 0.75)])
# DG.out_degree(1, weight='weight')

# DG.degree(1, weight='weight')

# print(list(DG.successors(1)))
# print(list(DG.neighbors(1)))
