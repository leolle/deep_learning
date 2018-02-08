# -*- coding: utf-8 -*-

# Python program to detect cycle
# in a graph

from collections import defaultdict
from ylib import ylog
import re
from lib.gftTools import gftIO
import os
import sys
import logging
from tqdm import tqdm
import time
import json
import networkx as nx

ylog.set_level(logging.DEBUG)
ylog.console_on()

graph = nx.read_gexf('whole_edges.rm_de.gexf')
ls_nodes = list(graph.nodes)
counter = 0
total_nodes_num = 287966
rm_counter = 0
while True:
    print('rm cycles loops number %s' % rm_counter)
    for node in tqdm(ls_nodes):
        try:
            # remove direct edge:
            ls_loop = nx.find_cycle(graph, node)
            # print(ls_loop)
            if len(ls_loop) == 2:
                if ls_loop[0][0] == ls_loop[1][1] and ls_loop[0][1] == ls_loop[1][0]:
                    graph.remove_edge(ls_loop[0][0], ls_loop[0][1])
            elif len(ls_loop) > 2:
                graph.remove_edge(ls_loop[-1][0], ls_loop[-1][1])
            # dict_loop[node].append(nx.find_cycle(G, node)[0])
            counter = 0
        except nx.NetworkXNoCycle:
            counter += 1
            pass
    if counter == (total_nodes_num - 1):
        break

    rm_counter += 1
nx.write_gexf(graph, 'whole_edges.no_loops.gexf')
