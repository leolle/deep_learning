# -*- coding: utf-8 -*-
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
import json

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

# ylog.set_level(logging.DEBUG)
# ylog.console_on()
# ylog.filelog_on("wiki_upload")
# ylog.debug("test")

client = MongoClient('mongodb://localhost:27017/')
db = client['wiki']
collection = db.zhwiki
batch_size = 20
# links number
# wiki_category_link line size = 1503
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
NODES_FAIL_MAX_RETRIES = 3
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (EncodeError, DecodeError, HTTPError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504, 111]
IGNORE_CATEGORIES = [
    '使用Catnav的页面', '缺少Wikidata链接的维基共享资源分类', '隐藏分类', '追踪分类', '维基百科特殊页面',
    '维基百科分类', '维基百科维护', '无需细分的分类', '不要删除的分类', '母分类', '全部重定向分类', '特殊条目'
]
EXAMPLE_CATEGORIES = ['深圳证券交易所上市公司', '上海证券交易所上市公司', '各证券交易所上市公司', '证券交易所', '证券']
EXAMPLE_CATEGORIES_PAGE_DICT = json.load(open('list.txt'))
# test fetch graph
test_url = 'http://192.168.1.166:9080'
# prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(test_url, test_user_name, test_pwd)


def test_get_skill_graph(args):
    try:
        graph = gftIO.get_graph_from_neo4j(
            '392482970E904D11190D208B7C22874A',
            server_url=test_url,
            user_name=test_user_name,
            pwd=test_pwd)
    except:
        pass


def delete_edge(dict_re_match_object):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    """
    uploaded_number = 0
    for index, value in dict_re_match_object.items():
        if value is not None:
            item = dict_re_match_object.get(index)
            edge_type = item.group(7)[1:-1]
            del_edge_type = None
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

                startNodeID_domain = "https://zh.wikipedia.org/wiki/Category:"
                startNodeID_primaryKeyInDomain = cat_title

                endNodeID_domain = "https://zh.wikipedia.org/wiki/"
                endNodeID_primaryKeyInDomain = page_title

                del_edge_type = "HasElement"

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
                subcat_title_zh = HanziConv.toSimplified(subcat_title)
                cat_title_zh = HanziConv.toSimplified(cat_title)
                startNodeID_domain = "https://zh.wikipedia.org/wiki/Category:"
                startNodeID_primaryKeyInDomain = cat_title
                endNodeID_domain = "https://zh.wikipedia.org/wiki/Category:"
                endNodeID_primaryKeyInDomain = subcat_title
                del_edge_type = "HasSubset"
            if del_edge_type is not None:
                start_node_pk = startNodeID_domain + "/" + startNodeID_primaryKeyInDomain
                end_node_pk = endNodeID_domain + "/" + endNodeID_primaryKeyInDomain
                start_node_hash = hashlib.md5(
                    start_node_pk.encode('utf-8')).hexdigest().upper()
                end_node_hash = hashlib.md5(
                    end_node_pk.encode('utf-8')).hexdigest().upper()
                get_or_else = ""
                get_source = ""
                get_target = ""
                edge_str = "|".join([
                    start_node_hash, end_node_hash, del_edge_type, get_or_else,
                    get_source, get_target
                ])
                edge_md5 = hashlib.md5(
                    edge_str.encode('utf-8')).hexdigest().upper()
                del_edge_type = None
                res = None
                error = None
                retry = 0
                while res is None:
                    try:
                        res = gs_call.delete_edge(edge_md5, False)
                    except GSError as e:
                        # error = 'edge not existed'
                        res = 'failed'
                        ylog.debug('failed  %s from %s to %s' %
                                   (edge_md5, start_node_hash, end_node_hash))
                    except HTTPError as e:
                        if e.code in RETRIABLE_STATUS_CODES:
                            error = 'A retriable HTTP error %d occurred:\n%s' % (
                                e.code, e.reason)
                        else:
                            raise
                    else:
                        res = 'success'
                        ylog.debug('deleted %s from %s to %s' %
                                   (edge_md5, start_node_hash, end_node_hash))

                    if error is not None:
                        print(error)
                        retry += 1
                        # res = None
                        if retry > MAX_RETRIES:
                            ylog.debug(res)
                            exit("no loger attempting to retry.")
                        max_sleep = 2**retry
                        sleep_seconds = random.random() * max_sleep
                        print('Sleeping %f seconds and then retrying...' %
                              sleep_seconds)
                        time.sleep(sleep_seconds)
                    if res == 'success':
                        uploaded_number += 1
                        ylog.debug('deleted %s from %s to %s' %
                                   (edge_md5, start_node_hash, end_node_hash))

    return uploaded_number


def upload_edge(dict_re_match_object):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    """
    res = None
    error = None
    retry = 0
    uploaded_number = 0
    while res is None:
        try:
            graph_upload_request = graphUpload_pb2.GraphUploadRequest()
            # iterate nodes batch
            for index, value in dict_re_match_object.items():
                if value is not None:
                    item = dict_re_match_object.get(index)
                    edge_type = item.group(7)[1:-1]
                    if edge_type == 'page':
                        page_title = item.group(3)[1:-1]
                        cat_title = item.group(2)[1:-1]
                        edge = graph_upload_request.graph.edges.add()
                        edge.props.type = "HasElement"
                        if '\\n' in cat_title:
                            end = cat_title.split("\\n")
                            cat_title = end[-1]
                        if '\\n' in page_title:
                            end = page_title.split("\\n")
                            page_title = end[-1]
                        page_title = page_title.replace(" ", "_")
                        page_title_zh = HanziConv.toSimplified(page_title)
                        cat_title_zh = HanziConv.toSimplified(cat_title)

                        edge.startNodeID.businessID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            cat_title)
                        # edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
                        # edge.startNodeID.primaryKeyInDomain = cat_title
                        # edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/"
                        # edge.endNodeID.primaryKeyInDomain = page_title
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
                        if subcat_title in IGNORE_CATEGORIES or cat_title in IGNORE_CATEGORIES:
                            continue
                        if subcat_title == cat_title:
                            continue
                        edge = graph_upload_request.graph.edges.add()
                        edge.props.type = "HasSubset"

                        # edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
                        # edge.startNodeID.primaryKeyInDomain = cat_title
                        # edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
                        # edge.endNodeID.primaryKeyInDomain = subcat_title

            graph_upload_request.uploadTag = "uploadWikiEdge"
            graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            res = gs_call.upload_graph(graph_upload_request)
        except HTTPError as e:
            if e.code in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.code,
                                                                     e.reason)
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
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)
    try:
        if res.edgeUpdateResultStatistics:
            ylog.debug(res.edgeUpdateResultStatistics)
            uploaded_number = res.edgeUpdateResultStatistics.numOfCreations + \
                res.edgeUpdateResultStatistics.numOfUpdates + \
                res.edgeUpdateResultStatistics.numOfSkips
        if res.failedEdges:
            for err in res.failedEdges:
                ylog.debug(err)
                ylog.debug(
                    "start node: %s" % err.edge.startNodeID.primaryKeyInDomain)
                ylog.debug(
                    "end node: %s" % err.edge.endNodeID.primaryKeyInDomain)
    except:
        pass

    return uploaded_number


def upload_page_node(dict_re_match_object):
    """ upload edge created from regular expression matched object.
    "(164,4,'模板消息','',263,0,0,0.134616506411337,'20171119123332','20171119123333',46122542,11752,'wikitext',NULL)"
    Keyword Arguments:
    re_match_object -- re object
    f               -- local file to write
    """
    res = None
    error = None
    re_upload_error = None
    retry = 0
    nodes_fail_retry = 0
    uploaded_number = 0
    while res is None:
        try:
            graph_upload_request = graphUpload_pb2.GraphUploadRequest()
            # iterate nodes batch
            for index, value in dict_re_match_object.items():
                if value is not None:
                    item = dict_re_match_object.get(index)
                    node = graph_upload_request.graph.nodes.add()
                    title = item.group(3)[1:-1]
                    try:
                        article = collection.find_one({"title": title})
                        page_content = article['text']
                        node.binaryContent = bytes(page_content, "utf-8")
                    except:
                        pass
                    node.props.type = "readonlyDoc"
                    node.subType = "HTML"
                    p1 = node.props.props.entries.add()
                    p1.key = "_s_import_source"
                    p1.value = "wiki"
                    p2 = node.props.props.entries.add()
                    p2.key = "_ownerid"
                    p2.value = "GFT"
                    p3 = node.props.props.entries.add()
                    p3.key = "_name"
                    p3.value = title
                    p4 = node.props.props.entries.add()
                    p4.key = "url"
                    p4.value = "https://zh.wikipedia.org/wiki/" + title

                    node.businessID.domain = "https://zh.wikipedia.org/wiki/"
                    node.businessID.primaryKeyInDomain = title
                    node.names.chinese = title

            # other information of the upload request
            graph_upload_request.uploadTag = "UploadWikiPageNodes"
            graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')

            res = gs_call.upload_graph(graph_upload_request)
        except HTTPError as e:
            if e.code in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.code,
                                                                     e.reason)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e
        try:
            if res.failedNodes:
                re_upload_error = "some nodes failed to upload %s" % res.failedNodeds
        except:
            pass
        if re_upload_error is not None:
            print(re_upload_error)
            nodes_fail_retry += 1
            res = None
            if nodes_fail_retry > NODES_FAIL_MAX_RETRIES:
                ylog.debug(res)
                res = "continue"
        if error is not None:
            print(error)
            retry += 1
            res = None
            if retry > MAX_RETRIES:
                ylog.debug(res)
                exit("no loger attempting to retry.")
            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)
    # jump out while response is None:
    try:
        if res.nodeUpdateResultStatistics:
            ylog.debug(res.nodeUpdateResultStatistics)
            uploaded_number = res.nodeUpdateResultStatistics.numOfCreations + \
                res.nodeUpdateResultStatistics.numOfUpdates + \
                res.nodeUpdateResultStatistics.numOfSkips
        if res.uploadedNodes:
            for updated in res.uploadedNodes:
                ylog.debug("uploaded node GID: %s" % updated.gid)
        if res.failedNodes:
            for err in res.failedNodes:
                if err.error.errorCode != 202001:
                    ylog.debug(err.error)
    except:
        pass
    return uploaded_number


def upload_cat_node(dict_re_match_object):
    """ upload node created from regular expression matched object.
    ('5', "'科学小作品'", '104', '12', '0')
    Keyword Arguments:
    re_match_object -- re object
    """
    res = None
    error = None
    re_upload_error = None
    retry = 0
    nodes_fail_retry = 0
    uploaded_number = 0
    while res is None:
        try:
            graph_upload_request = graphUpload_pb2.GraphUploadRequest()
            # iterate nodes batch
            for index, value in dict_re_match_object.items():
                if value is not None:
                    item = dict_re_match_object.get(index)
                    title = item.group(2)[1:-1]
                    zh_title = HanziConv.toSimplified(title)
                    if zh_title in IGNORE_CATEGORIES:
                        break
                    node = graph_upload_request.graph.nodes.add()
                    node.props.type = "Oset"
                    p1 = node.props.props.entries.add()
                    p1.key = "url"
                    p1.value = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                        title)
                    p2 = node.props.props.entries.add()
                    p2.key = "_s_import_source"
                    p2.value = "wiki"

                    # node.businessID.domain = "https://zh.wikipedia.org/wiki/Category:"
                    # node.businessID.primaryKeyInDomain = quote_plus(title)
                    node.businessID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                        title)
                    node.names.chinese = zh_title
            # other information of the upload request
            graph_upload_request.uploadTag = "UploadWikiCatNodes"
            graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')

            res = gs_call.upload_graph(graph_upload_request)

        except HTTPError as e:
            if e.code in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.code,
                                                                     e.reason)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e
        try:
            if res.failedNodes:
                re_upload_error = "some nodes failed to upload %s" % res.failedNodeds
        except:
            pass
        if re_upload_error is not None:
            print(re_upload_error)
            nodes_fail_retry += 1
            res = None
            if nodes_fail_retry > NODES_FAIL_MAX_RETRIES:
                ylog.debug(res)
                res = "continue"

        if error is not None:
            print(error)
            retry += 1
            res = None
            if retry > MAX_RETRIES:
                ylog.debug(res)
                exit("no loger attempting to retry.")
            max_sleep = 2**retry
            sleep_seconds = random.random() * max_sleep
            print('Sleeping %f seconds and then retrying...' % sleep_seconds)
            time.sleep(sleep_seconds)
    # ylog.debug(res)
    # jump out while response is None:
    try:
        if res.nodeUpdateResultStatistics:
            ylog.debug(res.nodeUpdateResultStatistics)
            uploaded_number = res.nodeUpdateResultStatistics.numOfCreations + \
                res.nodeUpdateResultStatistics.numOfUpdates + \
                res.nodeUpdateResultStatistics.numOfSkips
        if res.uploadedNodes:
            for updated in res.uploadedNodes:
                ylog.debug("uploaded node GID: %s" % updated.gid)
        if res.failedNodes:
            for err in res.failedNodes:
                if err.error.errorCode != 202001:
                    ylog.info(err.error)
                    ylog.debug(err.error)
    except:
        pass

    return uploaded_number


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
    uploaded_number = 0
    try:
        with open(file_path, 'r') as f:
            total_line_size = len(f.readlines())
        with open(file_path, 'r') as f:
            for i, line in enumerate(tqdm(f)):
                if i >= start and i <= end:
                    print("line #: %s/%s" % (i, total_line_size))
                    try:
                        last_span = re.search(line).span()[0]
                    except AttributeError:
                        continue
                    line_size = len(re.findall(line))
                    for i in tqdm(range(0, line_size, batch_size)):
                        # pause if find a file naed pause at the currend dir
                        while os.path.isfile('pause'):
                            time.sleep(100)
                            print("pause for 100 second")
                        re_batch = {}
                        for j in range(batch_size):
                            re_batch[j] = re.search(line, last_span)
                            if re_batch[j] is not None:
                                last_span = re_batch[j].span()[1]
                        uploaded_counter = func(re_batch)
                        uploaded_number += uploaded_counter

                elif i > end:
                    break

    except KeyboardInterrupt:
        print("uploaded number: %s" % uploaded_number)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    return uploaded_number
