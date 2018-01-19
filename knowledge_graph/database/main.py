# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import re
from lib.gftTools import gftIO
import graphUpload_pb2
from tqdm import tqdm
import os

batch_size = 100
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


def upload_edge(re_match_object):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    """
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()
    # edge from the first node to the second node
    edge = graph_upload_request.graph.edges.add()

    edge.props.type = "HasSubset"

    edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/"
    edge.startNodeID.primaryKeyInDomain = "word1"
    edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/"
    edge.endNodeID.primaryKeyInDomain = "word2"

    edge.subType = graphUpload_pb2.EdgeSubType.Value('PASS_REF')
    graph_upload_request.uploadTag = "testUpload"
    graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    response = gftIO.upload_graph(graph_upload_request, test_url,
                                  test_user_name, test_pwd)


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
    graph_upload_request.uploadTag = "testUpload"
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
    graph_upload_request.uploadTag = "testUpload"
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
        func(re_batch)
        uploaded_number = uploaded_number + batch_size
    return uploaded_number


if __name__ == '__main__':
    user_path = os.path.expanduser("~")
    category_path = user_path + "/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-category.zhs.sql"
    page_path = user_path + "/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-page.zhs.sql"
    category_sql = open(category_path, 'r')
    category = category_sql.read()
    category_sql.close()
    wiki_category_re = re.compile(
        "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
    wiki_category = wiki_category_re.findall(category)
    print("uploading wiki categories")
    uploaded_number = batch_upload(wiki_category_re, category,
                                   len(wiki_category), batch_size,
                                   upload_cat_node)
    print("uploaded number: %s, actual number in wiki: %s" %
          (uploaded_number, len(wiki_category)))
    del category
    page_sql = open(page_path, 'r')
    page = page_sql.read()
    page_sql.close()
    wiki_page_re = re.compile(
        "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
    )
    wiki_page = wiki_page_re.findall(page)
    print("uploading wiki page")
    uploaded_number = batch_upload(wiki_page_re, page,
                                   len(wiki_page), batch_size, upload_page_node)
    print("uploaded number: %s, actual number in wiki: %s" % (uploaded_number,
                                                              len(wiki_page)))
