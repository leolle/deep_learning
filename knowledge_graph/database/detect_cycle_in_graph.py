# -*- coding: utf-8 -*-

# Python program to detect cycle
# in a graph
import time
import re
from lib.gftTools import gftIO
from lib.gftTools.proto import graphUpload_pb2
from tqdm import tqdm
import random
from ylib import ylog
import logging
import os, sys
import hashlib
from google.protobuf.message import EncodeError
from urllib.error import HTTPError
from lib.gftTools.gftIO import GSError
from pymongo import MongoClient
from google.protobuf.message import DecodeError
from hanziconv import HanziConv
import networkx as nx

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on('remove_cycles')
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
NODES_FAIL_MAX_RETRIES = 3
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (EncodeError, DecodeError, HTTPError,
                        ConnectionResetError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504, 111]
IGNORE_CATEGORIES = [
    '使用Catnav的页面', '缺少Wikidata链接的维基共享资源分类', '隐藏分类', '追踪分类', '维基百科特殊页面',
    '维基百科分类', '维基百科维护', '无需细分的分类', '不要删除的分类', '母分类', '全部重定向分类', '特殊条目'
]

PY2 = sys.version_info[0] == 2
# Python 2.7 compatibiity
if PY2:
    from urllib import quote
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs
    from htmlentitydefs import name2codepoint
    from itertools import izip as zip, izip_longest as zip_longest
    range = xrange  # Use Python 3 equivalent
    chr = unichr  # Use Python 3 equivalent
    text_type = unicode

    class SimpleNamespace(object):

        def __init__(self, **kwargs):
            self.__dict__.update(kwargs)

        def __repr__(self):
            keys = sorted(self.__dict__)
            items = ("{}={!r}".format(k, self.__dict__[k]) for k in keys)
            return "{}({})".format(type(self).__name__, ", ".join(items))

        def __eq__(self, other):
            return self.__dict__ == other.__dict__
else:
    from urllib.parse import quote_plus, urlparse, parse_qs
    from urllib.parse import quote
    from html.entities import name2codepoint
    from itertools import zip_longest
    from types import SimpleNamespace
    text_type = str

# test fetch graph
# test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)

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


def add_edge(dict_re_match_object):
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
                graph.add_edge(cat_title, page_title, subtype=0)
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
                graph.add_edge(cat_title, subcat_title, subtype=1)


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
            line_start_position = 0
            line_end_position = len(line)
            # try to process the whole line in a wile loop until it's done
            while True:
                if i < start:
                    break
                elif i <= end:
                    try:
                        test_string = line[line_start_position:].decode('utf-8')
                        line_size = len(re.findall(test_string))

                    except UnicodeDecodeError as e:
                        line_end_position = e.start
                        ylog.debug('start at %s' % line_end_position)
                    finally:
                        string = line[line_start_position:
                                      line_end_position].decode('utf-8')
                        line_size = len(re.findall(string))
                        try:
                            last_span = re.search(string).span()[0]
                        except AttributeError:
                            break
                        line_size = len(re.findall(string))
                        for _ in range(0, line_size, batch_size):
                            # pause if find a file naed pause at the currend dir
                            re_batch = {}
                            for j in range(batch_size):
                                re_batch[j] = re.search(string, last_span)
                                if re_batch[j] is not None:
                                    last_span = re_batch[j].span()[1]
                            func(re_batch)
                        line_end_position = len(line)
                        line_start_position = line_end_position + 10
                else:
                    break


def write_graph(graph):
    """
    Keyword Arguments:
    graph --

    Return:
    list -- [(node1, node2, type)]
    """
    ls_edges = []
    for e in tqdm(graph.edges):
        node_from = e[0]
        node_to = e[1]
        edge_type = graph[node_from][node_to]['subtype']
        ls_edges.append(tuple([node_from, node_to, edge_type]))
    import pickle

    with open('graph.pkl', 'wb') as fp:
        pickle.dump(ls_edges, fp)
    return ls_edges


batch_upload(
    wiki_category_link_re,
    category_link_path,
    200,
    add_edge,
    start=0,
    end=10000)
# nx.write_yaml(graph, 'whole_edges.yaml')
# nx.write_gexf(graph, 'whole_edges.gexf')
# graph = nx.read_gexf('whole_edge.gexf')
ls_nodes = list(graph.nodes)
counter = 0
total_nodes_num = len(graph.nodes)
rm_counter = 0
try:
    while True:
        ylog.debug('rm cycles loops number %s' % counter)

        for node in tqdm(ls_nodes):
            removed_counter = 0
            # ylog.debug('rm cycles of node %s' % node)

            while True:
                try:
                    ls_loop = nx.find_cycle(graph, node)
                    removed_counter += 1
                    # remove direct edge:
                    #                    ylog.debug(ls_loop)
                    if len(ls_loop) == 2:
                        if ls_loop[0][0] == ls_loop[1][1] and ls_loop[0][1] == ls_loop[1][0]:
                            graph.remove_edge(ls_loop[0][0], ls_loop[0][1])
                    # remove big loop:
                    elif len(ls_loop) > 2:
                        graph.remove_edge(ls_loop[-1][0], ls_loop[-1][1])
                    elif len(ls_loop) == 1:
                        break
                        # remove all edges in the loop, then next create edge first in.
                        # for i in range(len(ls_loop) - 1):
                        #     graph.remove_edge(ls_loop[i + 1][0],
                        #                       ls_loop[i + 1][1])
                    # counter = 0
                except nx.NetworkXNoCycle:
                    counter += 1
                    if removed_counter != 0:
                        ylog.debug('rm cycles number %s' % removed_counter)
                    break

        break
except KeyboardInterrupt:
    # nx.write_gexf(graph, 'whole_edges.no_loops.gexf')
    try:
        sys.exit(0)
    except SystemExit:
        os._exit(0)
# nx.write_gexf(graph, 'whole_edges.no_loops.gexf')
ylog.debug('write graph')
ls_edges = write_graph(graph)
batch_size = 20


def upload_edge(ls_edges):
    """upload edge one by one
    Parameters:
    ls_edges -- list of edge tuples
    """
    len_edges = len(ls_edges)
    uploaded_number = 0
    batch_counter = 0
    for edge_counter in tqdm(range(0, len_edges, batch_size)):

        res = None
        error = None
        re_upload_error = None
        retry = 0
        nodes_fail_retry = 0
        graph_upload_request = graphUpload_pb2.GraphUploadRequest()
        while res is None:
            try:
                graph_upload_request = graphUpload_pb2.GraphUploadRequest()
                for e in ls_edges[batch_counter:batch_counter + batch_size]:
                    node_from = e[0]
                    node_to = e[1]
                    edge_type = e[2]
                    edge = graph_upload_request.graph.edges.add()

                    # page edge
                    if edge_type == 0:
                        edge.props.type = "HasElement"
                        edge.startNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            node_from)
                        edge.endNodeID.url = "https://zh.wikipedia.org/wiki/" + quote_plus(
                            node_to)
                # categories edge
                    else:
                        edge.startNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            node_from)
                        edge.endNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            node_to)
                        edge.props.type = "HasSubset"
                graph_upload_request.uploadTag = "uploadWikiEdge"
                graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                    'UPDATE')
                graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                    'UPDATE')
                res = gs_call.upload_graph(graph_upload_request)

            except HTTPError as e:
                if e.code in RETRIABLE_STATUS_CODES:
                    error = 'A retriable HTTP error %d occurred:\n%s' % (
                        e.code, e.reason)
                else:
                    raise
            except RETRIABLE_EXCEPTIONS as e:
                error = 'A retriable error occurred: %s' % e
            if error is not None:
                print(error)
                retry += 1
                res = None
                if retry > MAX_RETRIES:
                    ylog.debug(res)
                    exit("no loger attempting to retry.")
                max_sleep = 2**retry
                sleep_seconds = random.random() * max_sleep
                print(
                    'Sleeping %f seconds and then retrying...' % sleep_seconds)
                time.sleep(sleep_seconds)
        try:
            if res.edgeUpdateResultStatistics:
                ylog.debug(res.edgeUpdateResultStatistics)
                number = res.edgeUpdateResultStatistics.numOfCreations + \
                    res.edgeUpdateResultStatistics.numOfUpdates + \
                    res.edgeUpdateResultStatistics.numOfSkips
                uploaded_number += number
            if res.failedEdges:
                for err in res.failedEdges:
                    ylog.debug(err)
                    ylog.debug("start node: %s" %
                               err.edge.startNodeID.primaryKeyInDomain)
                    ylog.debug(
                        "end node: %s" % err.edge.endNodeID.primaryKeyInDomain)
        except:
            pass
        batch_counter += batch_size

    return uploaded_number


num = upload_edge(ls_edges)
ylog.log('upload edge number %s' % num)
