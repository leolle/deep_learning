# -*- coding: utf-8 -*-
import time
from lib.gftTools import gftIO
from lib.gftTools.proto import graphUpload_pb2
from tqdm import tqdm
import random
from ylib import ylog
import pickle
import os, sys
import hashlib
from google.protobuf.message import EncodeError
from urllib.error import HTTPError, URLError
from lib.gftTools.gftIO import GSError
from google.protobuf.message import DecodeError
from hanziconv import HanziConv
import json
from http.client import RemoteDisconnected

PY2 = sys.version_info[0] == 2
# Python 2.7 compatibiity
if PY2:
    from urllib import quote
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs
    from htmlentitydefs import name2codepoint
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

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
NODES_FAIL_MAX_RETRIES = 3
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (ConnectionResetError, RemoteDisconnected,
                        ConnectionRefusedError, URLError)
GRAPH_EXCEPTIONS = (EncodeError, DecodeError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504, 111]
with open('ignored_cat.pkl', 'rb') as fp:
    IGNORE_CATEGORIES = pickle.load(fp)

EXAMPLE_CATEGORIES_PAGE_DICT = json.load(open('list.txt'))
# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)


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
    """ delete edge regular expression object in the dictionary in a batch.
    1. get each value from the input dictionary.
    2. create a graph upload request.
    3. fill edge properties.
    set edge start node and end node.
    4. if there's any error upload response, retry.
    5. print upload statistics.
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
    """ upload edge regular expression object in the dictionary in a batch.
    1. get each value from the input dictionary.
    2. create a graph upload request.
    3. fill edge properties.
    set edge start node and end node.
    4. if there's any error upload response, retry.
    5. print upload statistics.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    (id, from, to,...)
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
                        page_title_zh = HanziConv.toSimplified(page_title)
                        cat_title_zh = HanziConv.toSimplified(cat_title)
                        # if not cat_title_zh in EXAMPLE_CATEGORIES_PAGE_DICT:
                        #     continue

                        edge = graph_upload_request.graph.edges.add()
                        edge.props.type = "HasElement"
                        edge.startNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            cat_title)
                        edge.endNodeID.url = "https://zh.wikipedia.org/wiki/" + quote_plus(
                            page_title)

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

                        # if not cat_title_zh in EXAMPLE_CATEGORIES_PAGE_DICT:
                        #     continue
                        if subcat_title_zh == cat_title_zh:
                            continue
                        edge = graph_upload_request.graph.edges.add()
                        edge.startNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            cat_title)
                        edge.endNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            subcat_title)
                        edge.props.type = "HasSubset"

            graph_upload_request.uploadTag = "uploadWikiEdge"
            graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            res = gs_call.upload_graph(graph_upload_request)
            # ylog.debug(res)
        except HTTPError as e:
            if e.code in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.code,
                                                                     e.reason)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e
        except GRAPH_EXCEPTIONS as e:
            break
        # try:
        #     if res.failedEdges:
        #         re_upload_error = "some nodes failed to upload %s" % res.failedEdges
        # except:
        #     pass
        # if re_upload_error is not None:
        #     print(re_upload_error)
        #     nodes_fail_retry += 1
        #     res = None
        #     if nodes_fail_retry > NODES_FAIL_MAX_RETRIES:
        #         ylog.debug(res)
        #         res = "continue"
        if error is not None:
            print(error)
            retry += 1
            res = None
            if retry > MAX_RETRIES:
                ylog.debug(res)
                ylog.debug("no loger attempting to retry.")
                error = None
                # exit("no loger attempting to retry.")
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


def upload_edge_from_graph(ls_edges, batch_size):
    """ upload edge regular expression object in the dictionary in a batch.
    1. get each value from the input dictionary.
    2. create a graph upload request.
    3. fill edge properties.
    set edge start node and end node.
    4. if there's any error upload response, retry.
    5. print upload statistics.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    (id, from, to,...)
    Keyword Arguments:
    re_match_object -- re object
    """
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

                    # page edge
                    if edge_type == 0:
                        edge = graph_upload_request.graph.edges.add()
                        edge.props.type = "HasElement"
                        edge.startNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                            node_from)
                        edge.endNodeID.url = "https://zh.wikipedia.org/wiki/" + quote_plus(
                            node_to)
                # categories edge
                    else:
                        if node_from in IGNORE_CATEGORIES:
                            continue
                        edge = graph_upload_request.graph.edges.add()
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
            except GRAPH_EXCEPTIONS as e:
                ylog.debug('A graph error occurred: %s' % e)
                break
            if error is not None:
                print(error)
                retry += 1
                res = None
                if retry > MAX_RETRIES:
                    ylog.debug(res)
                    # exit("no loger attempting to retry.")
                    ylog.debug("no loger attempting to retry.")
                    error = None
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
                    print(err)
                    print("start node: %s" %
                          err.edge.startNodeID.primaryKeyInDomain)
                    print(
                        "end node: %s" % err.edge.endNodeID.primaryKeyInDomain)
        except:
            pass
        batch_counter += batch_size

    return uploaded_number


# def upload_page_node(dict_re_match_object):
#     """ upload page regular expression object in the dictionary in a batch.
#     1. get each value from the input dictionary.
#     2. create a graph upload request.
#     3. fill node properties.
#     use encoded original Chinese title plus url as url property.
#     4. if there's any error upload response, retry.
#     5. print upload statistics.
#     "(164,4,'模板消息','',263,0,0,0.134616506411337,'20171119123332','20171119123333',46122542,11752,'wikitext',NULL)"
#     Keyword Arguments:
#     re_match_object -- re object, "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
#     f               -- local file to write
#     """
#     res = None
#     error = None
#     re_upload_error = None
#     retry = 0
#     nodes_fail_retry = 0
#     uploaded_number = 0
#     while res is None:
#         try:
#             graph_upload_request = graphUpload_pb2.GraphUploadRequest()
#             # iterate nodes batch
#             for index, value in dict_re_match_object.items():
#                 if value is not None:
#                     item = dict_re_match_object.get(index)
#                     node = graph_upload_request.graph.nodes.add()
#                     title = item.group(3)[1:-1]
#                     try:
#                         node.binaryContent = bytes(page_content, "utf-8")
#                     except:
#                         pass
#                     node.props.type = "readonlyDoc"
#                     node.subType = "HTML"
#                     p1 = node.props.props.entries.add()
#                     p1.key = "_s_import_source"
#                     p1.value = "wiki"
#                     p2 = node.props.props.entries.add()
#                     p2.key = "_ownerid"
#                     p2.value = "GFT"
#                     p3 = node.props.props.entries.add()
#                     p3.key = "_name"
#                     p3.value = title
#                     p4 = node.props.props.entries.add()
#                     p4.key = "url"
#                     p4.value = "https://zh.wikipedia.org/wiki/" + title

#                     # node.businessID.domain = "https://zh.wikipedia.org/wiki/"
#                     # node.businessID.primaryKeyInDomain = title
#                     node.names.chinese = title

#             # other information of the upload request
#             graph_upload_request.uploadTag = "UploadWikiPageNodes"
#             graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
#                 'UPDATE')
#             graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
#                 'UPDATE')

#             res = gs_call.upload_graph(graph_upload_request)
#         except HTTPError as e:
#             if e.code in RETRIABLE_STATUS_CODES:
#                 error = 'A retriable HTTP error %d occurred:\n%s' % (e.code,
#                                                                      e.reason)
#             else:
#                 raise
#         except RETRIABLE_EXCEPTIONS as e:
#             error = 'A retriable error occurred: %s' % e
#         try:
#             if res.failedNodes:
#                 re_upload_error = "some nodes failed to upload %s" % res.failedNodeds
#         except:
#             pass
#         if re_upload_error is not None:
#             print(re_upload_error)
#             nodes_fail_retry += 1
#             res = None
#             if nodes_fail_retry > NODES_FAIL_MAX_RETRIES:
#                 ylog.debug(res)
#                 res = "continue"
#         if error is not None:
#             print(error)
#             retry += 1
#             res = None
#             if retry > MAX_RETRIES:
#                 ylog.debug(res)
#                 exit("no loger attempting to retry.")
#             max_sleep = 2**retry
#             sleep_seconds = random.random() * max_sleep
#             print('Sleeping %f seconds and then retrying...' % sleep_seconds)
#             time.sleep(sleep_seconds)
#     # jump out while response is None:
#     try:
#         if res.nodeUpdateResultStatistics:
#             ylog.debug(res.nodeUpdateResultStatistics)
#             uploaded_number = res.nodeUpdateResultStatistics.numOfCreations + \
#                 res.nodeUpdateResultStatistics.numOfUpdates + \
#                 res.nodeUpdateResultStatistics.numOfSkips
#         if res.uploadedNodes:
#             for updated in res.uploadedNodes:
#                 ylog.debug("uploaded node GID: %s" % updated.gid)
#         if res.failedNodes:
#             for err in res.failedNodes:
#                 if err.error.errorCode != 202001:
#                     ylog.debug(err.error)
#     except:
#         pass
#     return uploaded_number


def upload_cat_node(dict_re_match_object):
    """ upload category regular expression object in the dictionary in a batch.
    1. get each value from the input dictionary.
    2. create a graph upload request.
    3. fill node properties.
    use encoded original Chinese title plus url as url property.
    4. if there's any error upload response, retry.
    5. print upload statistics.
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
                    # if zh_title in IGNORE_CATEGORIES:
                    #     break
                    node = graph_upload_request.graph.nodes.add()
                    node.props.type = "OSet"
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
                # break
                # exit("no loger attempting to retry.")
            ylog.debug(res)
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


def upload_node(dict_re_match_object):
    """ upload regular expression object in the dictionary in a batch.
    1. get each value from the input dictionary.
    2. create a graph upload request.
    3. fill node properties.
    use encoded original Chinese title plus url as url property.
    4. if there's any error upload response, retry.
    5. print upload statistics.
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
                    # print(item)
                    title = item.group()[1:-1]
                    zh_title = HanziConv.toSimplified(title)
                    # if zh_title in IGNORE_CATEGORIES:
                    #     break
                    node = graph_upload_request.graph.nodes.add()
                    node.props.type = "OSet"
                    # p1 = node.props.props.entries.add()
                    # p1.key = "url"
                    # p1.value = "https://www.google.com.hk/search?hl=en&source=hp&q=" + quote_plus(
                    #     title)
                    p2 = node.props.props.entries.add()
                    p2.key = "_s_import_source"
                    p2.value = "word2vec model"

                    node.businessID.url = "https://www.google.com.hk/search?hl=en&source=hp&q=" + quote_plus(
                        title)
                    node.names.chinese = zh_title

            # other information of the upload request
            graph_upload_request.uploadTag = "UploadWord2VecVocabNodes"
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
                # break
                # exit("no loger attempting to retry.")
            ylog.debug(res)
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
    """batch upload categories or edge.
    1. read sql file line by line.
    2. extract target string using regular expression.
    3. put these target content into a dictionary.
    4. use the upload function with dict as input.
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
        # UnicodeDecodeError: 'utf-8' codec can't decode byte 0xe5 in position 7629: invalid continuation byte

        with open(file_path, 'rb') as f:
            for i, line in enumerate(tqdm(f)):
                line_start_position = 0
                line_end_position = len(line)
                # try to process the whole line in a wile loop until it's done
                while True:
                    if i < start:
                        break

            #                 elif i <= end:
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
                            uploaded_count = func(re_batch)
                            uploaded_number += uploaded_count
                        line_end_position = len(line)
                        line_start_position = line_end_position + 10
                else:
                    break
    except KeyboardInterrupt:
        print("uploaded number: %s" % uploaded_number)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    return uploaded_number


def upload_single_edge(e):
    res = None
    error = None
    retry = 0
    while res is None:
        try:
            graph_upload_request = graphUpload_pb2.GraphUploadRequest()
            node_from = e[0]
            node_to = e[1]
            edge_type = e[2]

            if edge_type == 0:
                edge = graph_upload_request.graph.edges.add()
                edge.props.type = "HasElement"
                edge.startNodeID.url = "https://zh.wikipedia.org/wiki/Category:" + quote_plus(
                    node_from)
                edge.endNodeID.url = "https://zh.wikipedia.org/wiki/" + quote_plus(
                    node_to)
            # categories edge
            else:
                if node_from in IGNORE_CATEGORIES:
                    break
                edge = graph_upload_request.graph.edges.add()
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
            print(res)
        except HTTPError as e:
            if e.code in RETRIABLE_STATUS_CODES:
                error = 'A retriable HTTP error %d occurred:\n%s' % (e.code,
                                                                     e.reason)
            else:
                raise
        except RETRIABLE_EXCEPTIONS as e:
            error = 'A retriable error occurred: %s' % e
        except GRAPH_EXCEPTIONS as e:
            break

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
            ylog.debug(e)
        # if res.failedEdges:
        #     for err in res.failedEdges:
        #         print(err)
        #         print(
        #             "start node: %s" % err.edge.startNodeID.primaryKeyInDomain)
        #         print("end node: %s" % err.edge.endNodeID.primaryKeyInDomain)
    except:
        pass
