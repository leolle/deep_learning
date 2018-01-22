# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import time
import re
from lib.gftTools import gftIO
import graphUpload_pb2
from tqdm import tqdm
import random
from ylib import ylog
import logging
import os, sys
from google.protobuf.message import EncodeError
from urllib.error import HTTPError
ylog.set_level(logging.DEBUG)
# ylog.console_on()
ylog.filelog_on("wiki_upload")
batch_size = 300
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (EncodeError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504]
# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
try:
    graph = gftIO.get_graph_from_neo4j(
        '392482970E904D11190D208B7C22874A',
        server_url=prod_url,
        user_name=test_user_name,
        pwd=test_pwd)
except:
    pass


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
                        edge = graph_upload_request.graph.edges.add()
                        subcat_title = item.group(3)[1:-1]
                        cat_title = item.group(2)[1:-1]
                        if '\\n' in cat_title:
                            end = cat_title.split("\\n")
                            cat_title = end[-1]
                        if '\\n' in subcat_title:
                            end = subcat_title.split("\\n")
                            subcat_title = end[-1]
                        subcat_title = subcat_title.replace(" ", "_")
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
            res = gftIO.upload_graph(graph_upload_request, test_url,
                                     test_user_name, test_pwd)
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
            if res.failedEdges[0].error:
                ylog.debug(res.failedEdges[0])
                ylog.debug(
                    "start node: %s" % edge.startNodeID.primaryKeyInDomain)
                ylog.debug("end node: %s" % edge.endNodeID.primaryKeyInDomain)
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
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()

    # iterate nodes batch
    for index, value in dict_re_match_object.items():
        if value is not None:
            node = graph_upload_request.graph.nodes.add()
            title = dict_re_match_object.get(index).group(3)[1:-1]
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

    response = gftIO.upload_graph(graph_upload_request, test_url,
                                  test_user_name, test_pwd)

    return response


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

    response = gftIO.upload_graph(graph_upload_request, test_url,
                                  test_user_name, test_pwd)

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
    last_span = re.search(source).span()[0]
    for i in tqdm(range(0, source_len, batch_size)):
        re_batch = {}
        for j in range(batch_size):
            re_batch[j] = re.search(source, last_span)
            if re_batch[j] is not None:
                last_span = re_batch[j].span()[1]
        uploaded_counter = func(re_batch)
        uploaded_number = uploaded_number + uploaded_counter
    return uploaded_number


if __name__ == '__main__':
    try:
        user_path = os.path.expanduser("~")
        # category_path = user_path + "/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-category.zhs.sql"
        # page_path = user_path + "/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-page.zhs.sql"
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

        # upload edge

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
                                       category_link_size, batch_size,
                                       upload_edge)
        print("uploaded number: %s, actual number in wiki: %s" %
              (uploaded_number, category_link_size))
    except KeyboardInterrupt:
        print("uploaded number: %s, actual number in wiki: %s" %
              (uploaded_number, category_link_size))
        try:
            sys.exit(0)
        except SystemExit:
            os._exit(0)
