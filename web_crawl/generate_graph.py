# -*- coding: utf-8 -*-
"""
Wed May 16 09:45:38 CST 2018
generate webcrawl graph with searching words and related words.
"""
import networkx as nx
import copy
import logging
from tqdm import tqdm
from web_crawl.google_search.magic_google import MagicGoogle as GoogleSearch
from web_crawl.scholar.scholar import Scholar
import time

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

depth = 2
graph = nx.DiGraph()
base_nodes = []
end_nodes = []
i = 0
new_kw = 'nlp crawler'

# gs = GoogleSearch()
# data = gs.gain_data(query=new_kw, language='en', nums=10, pause=1)
scholar = Scholar()
data = scholar.gain_data('nlp', language='en', nums=10, pause=5)

base_nodes = data['related_keywords']
logging.debug('base nodes %s' % base_nodes)

#related_keywords = data['RelatedKeywords']
for kw in base_nodes:
    # base_nodes.append(kw)
    graph.add_edge(new_kw, kw)
# logging.debug(base_nodes)
while i < depth:
    for index, b in enumerate(base_nodes):
        # if b not in graph:
        if len(graph.out_edges(b)) == 0:
            logging.info('crawling %s' % b)
            data = gs.gain_data(query=b, language='en', nums=10, pause=2)
            nodes = data['related_keywords']
            if not nodes:
                continue
            # logging.debug('%s is already in graph' % b)
        else:
            nodes = []
        logging.debug("new nodes %s" % nodes)
        end_nodes.extend(nodes)
        if len(nodes) > 0:
            for n in nodes:
                graph.add_edge(b, n)
    base_nodes = copy.copy(end_nodes)
    logging.info('level %s nodes: %s' % (i, end_nodes))
    end_nodes = []
    i += 1

ls_nodes = list(graph.nodes)
total_nodes_num = len(graph.nodes)

# import matplotlib.pyplot as plt
# pos = nx.spring_layout(graph)
# nx.draw(
#     graph,
#     pos,
#     node_color='#A0CBE2',
#     width=4,
#     edge_cmap=plt.cm.Blues,
#     with_labels=False)
# plt.show()

nx.write_gexf(graph, new_kw + ".gexf")
