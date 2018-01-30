# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import re
from lib.gftTools import gftIO
from lib.gftTools.proto import graphUpload_pb2
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
# ylog.debug("test")
batch_size = 2
# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(test_url, test_user_name, test_pwd)
try:
    graph = gftIO.get_graph_from_neo4j(
        '392482970E904D11190D208B7C22874A',
        server_url=test_url,
        user_name=test_user_name,
        pwd=test_pwd)
except:
    pass

# read sql file
ylog.debug('reading sql files')
# category
category_path = "/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-category.zhs.sql"
category_sql = open(category_path, 'r')
category = category_sql.read()
category_sql.close()
wiki_category_re = re.compile(
    "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
wiki_category = wiki_category_re.findall(category)

# page
page_path = "/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-page.zhs.sql"
page_sql = open(page_path, 'r')
page = page_sql.read()
page_sql.close()
wiki_page_re = re.compile(
    "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
)
wiki_page = wiki_page_re.findall(page)

# links
# category_link_path = './zhwiki-latest-categorylinks.zhs.sql'
category_link_path = '/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.zhs.sql'
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)
category_link_sql = open(category_link_path, 'r')
category_link = category_link_sql.read()
category_link_sql.close()
wiki_category_link = wiki_category_link_re.findall(category_link)

# In [344]: len(wiki_category)
# Out[348]: 381500
# lines 68
# In [294]: len(wiki_category_link)
# Out[296]: 11942698
# page lines 7
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
del wiki_category_link
last_span = wiki_category_link_re.search(category_link).span()[0]
item = wiki_category_link_re.search(category_link, last_span)
last_span = wiki_category_link_re.search(category_link, last_span).span()[1]
graph_upload_request = graphUpload_pb2.GraphUploadRequest()
edge = graph_upload_request.graph.edges.add()
# edge from the first node to the second node
if item.group(7)[1:-1] == 'page':
    page_id = int(item.group(1))
    page_title = item.group(3)[1:-1]
    cat_title = item.group(2)[1:-1]
    if '\\n' in cat_title:
        end = cat_title.split("\\n")
        cat_title = end[-1]
    if '\\n' in page_title:
        end = page_title.split("\\n")
        page_title = end[-1]
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
response = gftIO.upload_graph(graph_upload_request, test_url, test_user_name,
                              test_pwd)
# print(item.group())
try:
    if response.failedEdges[0].error:
        print(response.failedEdges[0])
    if response.edgeUpdateResultStatistics:
        print(response.edgeUpdateResultStatistics)
except:
    pass
# XXX: fixed # TODO: add counter of successful uploaded edges.
ylog.debug('start uploading edges')
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
    if item.group(7)[1:-1] == 'subcat':
        cat_id = int(item.group(1))
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
        if response.edgeUpdateResultStatistics:
            ylog.debug(response.edgeUpdateResultStatistics)
            uploaded_number = response.edgeUpdateResultStatistics.numOfCreations + response.edgeUpdateResultStatistics.numOfUpdates + response.edgeUpdateResultStatistics.numOfSkips
            ylog.debug(uploaded_number)
        if response.failedEdges[0].error:
            ylog.debug(response.failedEdges[0])
            ylog.debug("start node: %s" % edge.startNodeID.primaryKeyInDomain)
            ylog.debug("end node: %s" % edge.endNodeID.primaryKeyInDomain)
    except:
        pass

# pk_str = "https://zh.wikipedia.org/wiki/Category:" + '/' + '隐藏分类'
# pk_md5 = hashlib.md5(pk_str.encode('utf-8')).hexdigest().upper()
# print(pk_md5)

# pk_str = "https://zh.wikipedia.org/wiki/" + '/' + '条码'
# pk_md5 = hashlib.md5(pk_str.encode('utf-8')).hexdigest().upper()
# print(pk_md5)


# # delete edge
# # s"${businessHashOfStartNode}|${businessHashOfEndNode}|${edgeType}|${edgeSubType.getOrElse("")}|${edgeInfo.getSource}|${edgeInfo.getTarget}"
# start_node_hash = "A688728DC925BF4CA5F63EC37E208DB4"
# end_node_hash = "6B75452A2D7376F338312670599EFCB5"
# edge_type = "dataflow"
# get_or_else = ""
# get_source = ""
# get_target = ""
# pk_str = "|".join([
#     start_node_hash, end_node_hash, edge_type, get_or_else, get_source,
#     get_target
# ])
# pk_md5 = hashlib.md5(pk_str.encode('utf-8')).hexdigest().upper()
# print(pk_md5)
def print_line(file_path):
    with open(file_path, 'r') as f:
        for i, line in enumerate(tqdm(f)):
            if len(line) > 100:
                pass
                # print('line %s, size %s' % (i, len(line)))


def open_file(path):
    with open(path) as f:
        for i, line in enumerate(f):
            print(len(line.readline()))


original = u'%E6%96%87%E5%AD%B8'
a = u'硝酸铵'
original_ch = u'文学'
import sys
if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs

result = quote_plus(a)

pk_str = "https://zh.wikipedia.org/wiki/" + result
# 数学
pk_str = "https://zh.wikipedia.org/wiki/%E6%95%B0%E5%AD%A6"
pk_md5 = hashlib.md5(pk_str.encode('utf-8')).hexdigest().upper()
print(hashlib.md5(pk_md5.encode("utf-8")).hexdigest())
text = gs_call.get_nodes_binary_data(['8FBBFADD256872063EF29034D6C1A86F'])
article = text.entries[0].data.data.decode('utf-8')
