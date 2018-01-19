# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import re
from lib.gftTools import gftIO
import skill_pb2
import graphUpload_pb2
from tqdm import tqdm
import time
import hashlib
from graph_upload import batch_upload
from graph_upload import upload_cat_node
from graph_upload import upload_page_node
from graph_upload import upload_edge
import logging
from ylib import ylog

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("wiki_upload")
ylog.debug("test")
batch_size = 2
# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
try:
    graph = gftIO.get_graph_from_neo4j(
        '392482970E904D11190D208B7C22874A',
        server_url=test_url,
        user_name=test_user_name,
        pwd=test_pwd)
except:
    pass

# read sql file
category_path = "./zhwiki-latest-category.zhs.sql"
category_link_path = './zhwiki-latest-categorylinks.zhs.sql'
page_path = "./zhwiki-latest-page.zhs.sql"
category_sql = open(category_path, 'r')
category = category_sql.read()
category_sql.close()
category_link_sql = open(category_link_path, 'r')
category_link = category_link_sql.read()
category_link_sql.close()
page_sql = open(page_path, 'r')
page = page_sql.read()
page_sql.close()

wiki_category_re = re.compile(
    "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
wiki_category = wiki_category_re.findall(category)
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)
wiki_page_re = re.compile(
    "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
)
wiki_page = wiki_page_re.findall(page)

wiki_category_link = wiki_category_link_re.findall(category_link)

print("uploading wiki categories")
uploaded_number = batch_upload(wiki_category_re, category,
                               len(wiki_category), batch_size, upload_cat_node)
print("uploaded number: %s, actual number in wiki: %s" % (uploaded_number,
                                                          len(wiki_category)))
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


def print_mdf5(wiki_list, position, category=True):
    for x in wiki_list:
        item_str = x[position][1:-1]
        print(item_str)
        if category:
            pk_str = "https://zh.wikipedia.org/wiki/Category:" + '/' + item_str
        else:
            pk_str = "https://zh.wikipedia.org/wiki/" + '/' + item_str
        pk_md5 = hashlib.md5(pk_str.encode('utf-8')).hexdigest().upper()
        print(pk_md5)


print_mdf5(wiki_category, 1, category=True)
print_mdf5(wiki_page, 2, category=False)

category_link_size = len(wiki_category_link)

last_span = wiki_category_link_re.search(category_link).span()[0]
for i in range(category_link_size):
    item = wiki_category_link_re.search(category_link, last_span)
    last_span = wiki_category_link_re.search(category_link, last_span).span()[1]
    # category to page link
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()
    edge = graph_upload_request.graph.edges.add()
    # edge from the first node to the second node
    if item.group(7)[1:-1] == 'page':
        page_id = int(item.group(1))
        page_title = item.group(3)[1:-1]
        cat_title = item.group(2)[1:-1]
        edge.props.type = "HasElement"

        edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
        edge.startNodeID.primaryKeyInDomain = cat_title
        edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/"
        edge.endNodeID.primaryKeyInDomain = page_title
    if item.group(7)[1:-1] == 'subcat':
        cat_id = int(item.group(1))
        subcat_title = item.group(3)[1:-1]
        cat_title = item.group(2)[1:-1]
        edge.props.type = "HasSubset"

        edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
        edge.startNodeID.primaryKeyInDomain = cat_title
        edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/Category:"
        edge.endNodeID.primaryKeyInDomain = subcat_title

    # edge.subType = graphUpload_pb2.EdgeSubType.Value('PASS_REF')
    graph_upload_request.uploadTag = "testUpload"
    graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    response = gftIO.upload_graph(graph_upload_request, test_url,
                                  test_user_name, test_pwd)
    # print(item.group())
    try:
        if response.failedEdges[0].error:
            print(response.failedEdges[0])
        if response.edgeUpdateResultStatistics:
            print(response.edgeUpdateResultStatistics)
    except:
        pass
