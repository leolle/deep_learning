# -*- coding: utf-8 -*-

# Python program to detect cycle
# in a graph

from collections import defaultdict
from ylib import ylog
import re
from lib.gftTools import gftIO
import os
import sys
from google.protobuf.message import EncodeError
from google.protobuf.message import DecodeError
from urllib.error import HTTPError
from urllib.error import URLError
from pymongo import MongoClient
# from graph_upload import batch_upload, upload_edge, upload_cat_node, upload_page_node, delete_edge
import logging
from tqdm import tqdm
import time

ylog.set_level(logging.DEBUG)
# ylog.console_on()

ylog.filelog_on("wiki_upload")


class Graph():

    def __init__(self):
        self.graph = defaultdict(list)
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
                if visited[neighbour] == False:
                    if self.isCyclicUtil(neighbour, visited, recStack) == True:
                        return True

                    elif recStack[neighbour] == True:
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
            if visited[node] == False:
                if self.isCyclicUtil(node, visited, recStack) == True:
                    return True
        return False

    def direct_loop(self):
        for node in self.graph.keys():
            if node in self.graph[node]:
                #                 ylog.debug("%s" % node)
                print("%s" % node)


g = Graph()
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
    category_link_path = user_path + '/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.zhs.sql'

# category_link_path = './data/zhwiki-latest-categorylinks.zhs.sql'
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)


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
                g.addEdge(cat_title, subcat_title)


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
    with open(file_path, 'r') as f:
        for i, line in enumerate(tqdm(f)):
            #         print("line #: %s/%s" % (i, 1503))
            #         print(len(line))
            # print(g.graph.keys())
            if i < start:
                continue
            if i <= end:
                # print("line #: %s/%s" % (i, 1503))
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
    # print(g.graph.keys())


batch_upload(
    wiki_category_link_re,
    category_link_path,
    200,
    upload_edge,
    start=44,
    end=1503)
g.direct_loop()
# if g.isCyclic() == 1:
#     print("Graph has a cycle")
# else:
#     print("Graph has no cycle")
