# -*- coding: utf-8 -*-

# Python program to detect cycle
# in a graph

from collections import defaultdict
from ylib import ylog
import re
from lib.gftTools import gftIO
import os
import sys
# from graph_upload import batch_upload, upload_edge, upload_cat_node, upload_page_node, delete_edge
import logging
from tqdm import tqdm
import time
import json
import networkx as nx

ylog.set_level(logging.DEBUG)
ylog.console_on()

# ylog.filelog_on("wiki_upload")

# EXAMPLE_CATEGORIES = ['深圳证券交易所上市公司', '上海证券交易所上市公司', '各证券交易所上市公司', '证券交易所', '证券']
# dict_company = json.load(open('list.txt'))
# ls_company = open('listed_company.txt', 'w')
# for comp in dict_company['上海证券交易所上市公司']:
#     ls_company.write(comp + '\n')
# for comp in dict_company['深圳证券交易所上市公司']:
#     ls_company.write(comp + '\n')
# ls_company.close()


class Graph():

    def __init__(self):
        self.graph = defaultdict(list)
        self.loop = defaultdict(list)
        # self.graph = {}

    def addEdge(self, u, v):
        self.graph[u].append(v)
        # self.graph[u].update(v)

    def isCyclicUtil(self, v, visited, recStack):

        # Mark current node as visited and
        # adds to recursion stack
        visited[v] = True
        recStack[v] = True

        # Recur for all neighbours
        # if any neighbour is visited and in
        # recStack then graph is cyclic
        for neighbour in self.graph[v]:
            try:
                if visited[neighbour] is False:
                    if self.isCyclicUtil(neighbour, visited, recStack) is True:
                        return True

                    elif recStack[neighbour] is True:
                        return True
            except KeyError:
                pass
        # The node needs to be poped from
        # recursion stack before function ends
        recStack[v] = False
        return False

    # Returns true if graph is cyclic else false
    def isCyclic(self):
        #         visited = [False] * self.graph.keys()
        #         recStack = [False] * self.graph.keys()
        visited = dict.fromkeys(self.graph, False)
        recStack = dict.fromkeys(self.graph, False)
        print('visited')
        print(visited)
        for node in self.graph.keys():
            print(node)
            if visited[node] is False:
                if self.isCyclicUtil(node, visited, recStack) is True:
                    return True
        return False

    def self_loop(self):
        for node in self.graph.keys():
            if node in self.graph[node]:
                #                 ylog.debug("%s" % node)
                print("%s" % node)

    def direct_loop(self,):
        for node in self.graph.keys():
            for element in self.graph[node]:
                if element in self.graph.keys():
                    if node in self.graph[element]:
                        self.loop[node].append(element)
                        print("(%s, %s), (%s, %s)" % (node, element, element,
                                                      node))


# g.addEdge(0, 1)
# g.addEdge(0, 2)
# g.addEdge(1, 2)
# # g.addEdge(2, 0)
# g.addEdge(3, 4)
# g.addEdge(3, 3)
user_path = os.path.expanduser("~")
try:
    category_link_path = sys.argv[1]
except:
    category_link_path = user_path + \
        '/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.sql'
else:
    category_link_path = user_path + \
        '/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.sql'
# category_link_path = './data/zhwiki-latest-categorylinks.zhs.sql'
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)
graph = nx.DiGraph()


def upload_edge(dict_re_match_object):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    """
    # iterate nodes batch
    for index, value in dict_re_match_object.items():
        if value is not None:
            item = dict_re_match_object.get(index)
            edge_type = item.group(7)[1:-1]
            if edge_type == 'page':
                page_title = item.group(3)[1:-1]
                cat_title = item.group(2)[1:-1]
                if '\\n' in cat_title:
                    end = cat_title.split("\\n")
                    cat_title = end[-1]
                if '\\n' in page_title:
                    end = page_title.split("\\n")
                    page_title = end[-1]
                page_title = page_title.replace(" ", "_")
                # ylog.debug(cat_title)
                # ylog.debug(subcat_title)
                # if cat_title in EXAMPLE_CATEGORIES:
                graph.add_edge(cat_title, page_title, subtype='page')
            if edge_type == 'subcat':
                subcat_title = item.group(3)[1:-1]
                cat_title = item.group(2)[1:-1]
                if '\\n' in cat_title:
                    end = cat_title.split("\\n")
                    cat_title = end[-1]
                if '\\n' in subcat_title:
                    end = subcat_title.split("\\n")
                    subcat_title = end[-1]
                subcat_title = subcat_title.replace(" ", "_")
                # ylog.debug(cat_title)
                # ylog.debug(subcat_title)
                if subcat_title == cat_title:
                    continue
                graph.add_edge(cat_title, subcat_title, subtype='subcat')


#                g.addEdge(cat_title, subcat_title)
# if cat_title in EXAMPLE_CATEGORIES:


def batch_upload(re, file_path, batch_size, func, start, end):
    """batch upload categories or page
    Keyword Arguments:
    re         -- regular expression
    source     -- file path
    batch_size --
    func       -- upload function
    start      -- start position
    end        -- end position

    """
    # with open(file_path, 'r') as f:
    #     print("reading all lines from sql")
    #     total_line_size = len(f.readlines())
    with open(file_path, 'rb') as f:
        for i, line in enumerate(tqdm(f)):
            #         print("line #: %s/%s" % (i, 1503))
            #         print(len(line))
            # print(g.graph.keys())
            # print("line #: %s/%s" % (i, 1503))
            try:
                if i < start:
                    continue
                if i <= end:
                    line = line.decode('utf-8')
                    try:
                        last_span = re.search(line).span()[0]
                    except AttributeError:
                        continue
                    line_size = len(re.findall(line))
                    # ylog.debug(line_size)
                    for i in range(0, line_size, batch_size):
                        # pause if find a file naed pause at the currend dir
                        re_batch = {}
                        for j in range(batch_size):
                            re_batch[j] = re.search(line, last_span)
                            if re_batch[j] is not None:
                                last_span = re_batch[j].span()[1]
                        func(re_batch)
                else:
                    break
            except UnicodeDecodeError as e:
                last_span = e.start + 10
                line_size = len(re.findall(line))
                ylog.debug(line_size)
                for i in range(0, line_size, batch_size):
                    # pause if find a file naed pause at the currend dir
                    re_batch = {}
                    for j in range(batch_size):
                        re_batch[j] = re.search(line, last_span)
                        if re_batch[j] is not None:
                            last_span = re_batch[j].span()[1]
                    func(re_batch)

    # print(g.graph.keys())


g = Graph()
batch_upload(
    wiki_category_link_re,
    category_link_path,
    200,
    upload_edge,
    start=960,
    end=1503)
# graph = nx.read_gexf('whole_edge.gexf')
nx.write_gexf(graph, 'whole_edges.gexf')
ls_nodes = list(graph.nodes)
counter = 0
total_nodes_num = 287966
rm_counter = 0
try:
    while True:
        ylog.debug('rm cycles loops number %s' % counter)

        for node in tqdm(ls_nodes):
            removed_counter = 0
            ylog.debug('rm cycles of node %s' % node)

            while True:
                try:
                    ls_loop = nx.find_cycle(graph, node)
                    # remove direct edge:
                    ylog.debug(ls_loop)
                    if len(ls_loop) == 2:
                        if ls_loop[0][0] == ls_loop[1][1] and ls_loop[0][1] == ls_loop[1][0]:
                            graph.remove_edge(ls_loop[0][0], ls_loop[0][1])
                    # remove big loop:
                    elif len(ls_loop) > 2:
                        graph.remove_edge(ls_loop[-1][0], ls_loop[-1][1])
                        # remove all edges in the loop, then next create edge first in.
                        # for i in range(len(ls_loop) - 1):
                        #     graph.remove_edge(ls_loop[i + 1][0],
                        #                       ls_loop[i + 1][1])
                    # counter = 0
                    removed_counter += 1
                except nx.NetworkXNoCycle:
                    counter += 1
                    if removed_counter != 0:
                        ylog.debug('rm cycles number %s' % removed_counter)
                    break

        if counter >= total_nodes_num - 1:
            break
except KeyboardInterrupt:
    nx.write_gexf(graph, 'whole_edges.no_loops.gexf')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
nx.write_gexf(graph, 'whole_edges.no_loops.gexf')

# ls_nodes = list(graph.nodes)

# g.direct_loop()
# g.self_loop()
# print(nx.find_cycle(graph, ls_nodes[4]))

# ls_nodes = list(graph.nodes)
# dict_loop = defaultdict(list)
# # for node in tqdm(ls_nodes):
# #     try:
# #         # remove direct edge:
# #         ls_loop = nx.find_cycle(graph, node)
# #         # print(ls_loop)
# #         if len(ls_loop) == 2:
# #             if ls_loop[0][0] == ls_loop[1][1] and ls_loop[0][1] == ls_loop[1][0]:
# #                 graph.remove_edge(ls_loop[0][0], ls_loop[0][1])
# #         # dict_loop[node].append(nx.find_cycle(G, node)[0])
# #     except nx.NetworkXNoCycle:
# #         pass
# """save graph removed direct cycle edge."""
# # nx.write_gexf(graph, 'whole_edges.rm_di.gexf')

# graph = nx.read_gexf('whole_edges.rm_de.gexf')
# ls_nodes = list(graph.nodes)

# # for node in tqdm(ls_nodes):
# #     try:
# #         # remove direct edge:
# #         ls_loop = nx.find_cycle(graph, node)
# #         # print(ls_loop)
# #         if len(ls_loop) > 2:
# #             graph.remove_edge(ls_loop[-1][0], ls_loop[-1][1])
# #         # dict_loop[node].append(nx.find_cycle(G, node)[0])
# #     except nx.NetworkXNoCycle:
# #         pass
# # """save graph removed last edge in the cycle."""
# # nx.write_gexf(graph, 'whole_edges.rm_de.gexf')

# #    start=44,
# #    end=1503)
# # ls_cycle = list(nx.simple_cycles(G))
# # file_cycle = open('cycle.txt', 'w')
# # for loop in ls_cycle:
# #     print(loop)
# #     for i in loop:
# #         file_cycle.write(i + '\t')
# #     file_cycle.write('\n')
# # file_cycle.close()
# # for comp in dict_company['上海证券交易所上市公司']:
# #     ls_company.write(comp + '\n')
# # for comp in dict_company['深圳证券交易所上市公司']:
# #     ls_company.write(comp + '\n')
# # ls_company.close()

# # G = nx.DiGraph([(0, 1), (0, 2), (1, 2), (2, 1)])
# # try:
# #     nx.find_cycle(G, orientation='original')
# # except:
# #     pass
# # a = list(nx.find_cycle(G, orientation='ignore'))

# # import matplotlib.pyplot as plt
# # nx.draw_networkx(G)
# # plt.show()
# # with open(category_link_path, 'rb') as f:
# #     for i, line in enumerate(tqdm(f)):
# #         #         print("line #: %s/%s" % (i, 1503))
# #         #         print(len(line))
# #         # print(g.graph.keys())
# #         # print("line #: %s/%s" % (i, 1503))
# #         try:
# #             line = line.decode('utf-8')
# # #            print(line[10:100])

# #         except UnicodeDecodeError as e:
# #             print('Line: {}, Offset: {}, {}'.format(i, e.start, e.reason))
# #             print(line[e.start:(e.start + 100)])
# #             print(line[e.start:e.end])
# #             pass
# # for node in ls_nodes:
# #     try:
# #         print(nx.find_cycle(graph, node))
# #     except nx.NetworkXNoCycle:
# #         pass
# for node in tqdm(ls_nodes):
#     try:
#         # remove direct edge:
#         ls_loop = nx.find_cycle(graph, node)
#         # print(ls_loop)
#         if len(ls_loop) == 2:
#             if ls_loop[0][0] == ls_loop[1][1] and ls_loop[0][1] == ls_loop[1][0]:
#                 graph.remove_edge(ls_loop[0][0], ls_loop[0][1])
#         # dict_loop[node].append(nx.find_cycle(G, node)[0])
#     except nx.NetworkXNoCycle:
#         pass
