# -*- coding: utf-8 -*-
import time
import re
from lib.gftTools import gftIO
import graphUpload_pb2
from tqdm import tqdm
import random
from ylib import ylog
import logging
import os, sys
import hashlib
from google.protobuf.message import EncodeError
from urllib.error import HTTPError
from lib.gftTools.gftIO import GSError

ylog.set_level(logging.DEBUG)
# ylog.console_on()
ylog.filelog_on("wiki_upload")
batch_size = 20
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (EncodeError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
IGNORE_CATEGORIES = [
    '使用Catnav的页面', '缺少Wikidata链接的维基共享资源分类', '隐藏分类', '追踪分类', '维基百科特殊页面',
    '维基百科分类', '维基百科维护', '无需细分的分类', '不要删除的分类', '母分类', '全部重定向分类', '特殊条目'
]
# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(test_url, test_user_name, test_pwd)
try:
    graph = gftIO.get_graph_from_neo4j(
        '392482970E904D11190D208B7C22874A',
        server_url=prod_url,
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
                        ylog.debug('failed  %s from %s to %s' %
                                   (edge_md5, start_node_hash, end_node_hash))
                    except HTTPError as e:
                        if e.code in RETRIABLE_STATUS_CODES:
                            error = 'A retriable HTTP error %d occurred:\n%s' % (
                                e.code, e.reason)
                        else:
                            raise
                    finally:
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
                    else:
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
                        edge = graph_upload_request.graph.edges.add()
                        page_title = item.group(3)[1:-1]
                        cat_title = item.group(2)[1:-1]
                        edge.props.type = "HasElement"
                        if '\\n' in cat_title:
                            end = cat_title.split("\\n")
                            cat_title = end[-1]
                        if '\\n' in page_title:
                            end = page_title.split("\\n")
                            page_title = end[-1]
                        page_title = page_title.replace(" ", "_")

                        edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
                        edge.startNodeID.primaryKeyInDomain = cat_title
                        edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/"
                        edge.endNodeID.primaryKeyInDomain = page_title
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
                        edge = graph_upload_request.graph.edges.add()
                        edge.props.type = "HasSubset"

                        edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
                        edge.startNodeID.primaryKeyInDomain = cat_title
                        edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
                        edge.endNodeID.primaryKeyInDomain = subcat_title

            graph_upload_request.uploadTag = "uploadWikiEdge"
            graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
                'UPDATE')
            res = gs_call.upload_graph(graph_upload_request)
            # if response is not None:
            #     print("successfully uploaded")
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
            uploaded_number = res.edgeUpdateResultStatistics.numOfCreations + res.edgeUpdateResultStatistics.numOfUpdates + res.edgeUpdateResultStatistics.numOfSkips
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
    retry = 0
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
                    node.props.type = "readonlyDoc"
                    p0 = node.props.props.entries.add()
                    p0.key = "_sys_subtype"
                    p0.value = "HTML"
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
            # if response is not None:
            #     print("successfully uploaded")
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
    # jump out while response is None:
    try:
        if res.nodeUpdateResultStatistics:
            ylog.debug(res.nodeUpdateResultStatistics)
            uploaded_number = res.nodeUpdateResultStatistics.numOfCreations + res.nodeUpdateResultStatistics.numOfUpdates + res.nodeUpdateResultStatistics.numOfSkips
        if res.failedNode:
            for err in res.failedNode:
                ylog.debug(err)
                # ylog.debug(
                #     "start node: %s" % err.edge.startNodeID.primaryKeyInDomain)
                # ylog.debug(
                #     "end node: %s" % err.edge.endNodeID.primaryKeyInDomain)
    except:
        pass

    return uploaded_number


def upload_cat_node(dict_re_match_object):
    """ upload node created from regular expression matched object.
    ('5', "'科学小作品'", '104', '12', '0')
    Keyword Arguments:
    re_match_object -- re object
    """
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()
    # iterate nodes batch
    for index, value in dict_re_match_object.items():
        if value is not None:
            node = graph_upload_request.graph.nodes.add()
            node.props.type = "OSet"
            title = dict_re_match_object.get(index).group(2)[1:-1]
            p0 = node.props.props.entries.add()
            p0.key = "_name"
            p0.value = title
            p1 = node.props.props.entries.add()
            p1.key = "url"
            p1.value = "https://zh.wikipedia.org/wiki/Category:" + title
            p2 = node.props.props.entries.add()
            p2.key = "_s_import_source"
            p2.value = "wiki"
            p3 = node.props.props.entries.add()
            p3.key = "_ownerid"
            p3.value = "GFT"

            node.businessID.domain = "https://zh.wikipedia.org/wiki/Category:"
            node.businessID.primaryKeyInDomain = title

            node.names.chinese = title
    # other information of the upload request
    graph_upload_request.uploadTag = "UploadWikiCategoryNodes"
    graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')

    response = gs_call.upload_graph(graph_upload_request)

    return response


def batch_upload(re, source, source_len, batch_size, func):
    """batch upload categories or page
    Keyword Arguments:
    re         -- regular expression
    source     -- str read from file
    source_len -- the size of items
    batch_size --
    func       -- upload function
    """
    uploaded_number = 0
    try:
        last_span = re.search(source).span()[0]
        for i in tqdm(range(0, source_len, batch_size)):
            while os.path.isfile('pause'):
                time.sleep(100)
                print("pause for 100 second")
            re_batch = {}
            for j in range(batch_size):
                re_batch[j] = re.search(source, last_span)
                if re_batch[j] is not None:
                    last_span = re_batch[j].span()[1]
            uploaded_counter = func(re_batch)
            uploaded_number += uploaded_counter
    except KeyboardInterrupt:
        print("uploaded number: %s" % uploaded_number)
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
    return uploaded_number


if __name__ == '__main__':
    user_path = os.path.expanduser("~")
    # category_path = user_path + "/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-category.zhs.sql"
    # # open category sql file
    # category_sql = open(category_path, 'r')
    # category = category_sql.read()
    # category_sql.close()
    # wiki_category_re = re.compile(
    #     "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
    # wiki_category = wiki_category_re.findall(category)
    # print("uploading wiki categories")
    # uploaded_number = batch_upload(wiki_category_re, category,
    #                                len(wiki_category), batch_size,
    #                                upload_cat_node)
    # print("uploaded number: %s, actual number in wiki: %s" %
    #       (uploaded_number, len(wiki_category)))
    # del category
    # del wiki_category

    # # open page sql file
    # page_path = user_path + "/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-page.zhs.sql"
    # page_sql = open(page_path, 'r')
    # page = page_sql.read()
    # page_sql.close()
    # wiki_page_re = re.compile(
    #     "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
    # )
    # wiki_page = wiki_page_re.findall(page)
    # print("uploading wiki page")
    # uploaded_number = batch_upload(wiki_page_re, page,
    #                                len(wiki_page), batch_size, upload_page_node)
    # print("uploaded number: %s, actual number in wiki: %s" % (uploaded_number,
    #                                                           len(wiki_page)))
    # del wiki_page
    # del page

    # # upload edge

    category_link_path = './data/zhwiki-latest-categorylinks.zhs.sql'
    wiki_category_link_re = re.compile(
        "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
    )

    ylog.debug('reading link sql file')
    category_link_sql = open(category_link_path, 'r')
    category_link = category_link_sql.read()
    wiki_category_link = wiki_category_link_re.findall(category_link)
    ylog.debug('close link sql file')
    category_link_sql.close()
    category_link_size = len(wiki_category_link)
    del wiki_category_link
    ylog.debug("uploading wiki categorie page link")
    uploaded_number = batch_upload(wiki_category_link_re, category_link,
                                   category_link_size, batch_size, delete_edge)
    print("uploaded number: %s, actual number in wiki: %s" %
          (uploaded_number, category_link_size))
