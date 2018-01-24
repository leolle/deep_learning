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
batch_size = 100
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
    "\(([0-9]+),('[^,]+'),('[^,]+'),('[^,]+'),('[^,]+|'),('[^,]+'),('[^,]+')\)")
wiki_page_re = re.compile(
    "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
)
wiki_page = wiki_page_re.findall(page)

wiki_category_link = re.findall(wiki_category_re, category)
edge = wiki_category_link_re.search(category_link)

# wiki = wiki_content.search(lines)
# for i in range(len(all_matched_content)):
# last_span = wiki_page_re.search(page).span()[1]


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
            title = dict_re_match_object.get(index).group(2)[1:-1]
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

            node.props.type = "Oset"
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
    # if response.failed
    return response


def batch_upload_cat():
    last_span = wiki_category_re.search(category).span()[1]
    for i in tqdm(range(0, len(wiki_category), batch_size)):
        re_batch = {}
        for j in range(batch_size):
            re_batch[j] = wiki_category_re.search(category, last_span)
            if re_batch[j] is not None:
                last_span = re_batch[j].span()[1]
        upload_cat_node(re_batch)


def batch_upload_page():
    last_span = wiki_page_re.search(page).span()[1]
    for i in tqdm(range(0, len(wiki_page), batch_size)):
        # for i in tqdm(range(0, 4)):
        re_batch = {}
        for j in range(batch_size):
            re_batch[j] = wiki_page_re.search(page, last_span)
            if re_batch[j] is not None:
                last_span = re_batch[j].span()[1]
        res = upload_page_node(re_batch)


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
        # for i in tqdm(range(0, 4)):
        re_batch = {}
        for j in range(batch_size):
            re_batch[j] = re.search(source, last_span)
            if re_batch[j] is not None:
                last_span = re_batch[j].span()[1]
        func(re_batch)
        uploaded_number = uploaded_number + batch_size
    return uploaded_number


if __name__ == '__main__':
    category_path = "/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-category.zhs.sql"
    page_path = "/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-page.zhs.sql"
    category_sql = open(category_path, 'r')
    category = category_sql.read()
    category_sql.close()
    wiki_category_re = re.compile(
        "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
    wiki_category = wiki_category_re.findall(category)
    print("uploading wiki categories")
    # uploaded_number = batch_upload(wiki_category_re, category,
    #                                len(wiki_category), batch_size,
    #                                upload_cat_node)
    # print("uploaded number: %s, actual number in wiki: %s" %
    #       (uploaded_number, len(wiki_category)))
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

last_span = wiki_category_re.search(category).span()[0]
# for i in tqdm(range(len(wiki_category))):
for i in tqdm(range(5)):
    content = wiki_category_re.search(category, last_span)
    last_span = content.span()[1]
    # print(content.group(0))
    res = upload_cat_node(content)

# Write the new wiki to disk.
# with open('wiki.proto', "wb") as f:
#    f.write(wiki_node.SerializeToString())

# groups = re.findall("\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)",
#                     category)
# # In[80]: len(groups)
# # Out[81]: 381500
# graph_upload_request = graphUpload_pb2.GraphUploadRequest()

# # iterate nodes batch
# node = graph_upload_request.graph.nodes.add()

# node.props.type = "Oset"
# title = re_batch.get(0).group(2)[1:-1]
# p0 = node.props.props.entries.add()
# p0.key = "cat_title"
# p0.value = title
# p1 = node.props.props.entries.add()
# p1.key = "url"
# p1.value = "https://zh.wikipedia.org/wiki/Category:" + title

# node.businessID.domain = "https://zh.wikipedia.org/wiki/"
# node.businessID.primaryKeyInDomain = title

# node.names.chinese = title
# # other information of the upload request
# graph_upload_request.uploadTag = "testUpload"
# graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
#     'UPDATE')
# graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
#     'UPDATE')

# response = gftIO.upload_graph(graph_upload_request, test_url, test_user_name,
#                               test_pwd)
# graph_upload_request = graphUpload_pb2.GraphUploadRequest()
# node = graph_upload_request.graph.nodes.add()
# title = page.group(3)[1:-1]
# node.props.type = "readonlyDoc"
# p0 = node.props.props.entries.add()
# p0.key = "_sys_subtype"
# p0.value = "HTML"
# p1 = node.props.props.entries.add()
# p1.key = "_s_import_source"
# p1.value = "wiki"
# p2 = node.props.props.entries.add()
# p2.key = "_ownerid"
# p2.value = "GFT"
# p3 = node.props.props.entries.add()
# p3.key = "_name"
# p3.value = title
# p4 = node.props.props.entries.add()
# p4.key = "url"
# p4.value = "https://zh.wikipedia.org/wiki/" + title

# node.businessID.domain = "https://zh.wikipedia.org/wiki/"
# node.businessID.primaryKeyInDomain = title

# node.names.chinese = title
# # other information of the upload request
# graph_upload_request.uploadTag = "testUpload"
# graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
#     'UPDATE')
# graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
#     'UPDATE')

# response = gftIO.upload_graph(graph_upload_request, test_url, test_user_name,
#                               test_pwd)
category_link_path = '/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.zhs.sql'
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)
category_link_sql = open(category_link_path, 'r')
category_link = category_link_sql.read()
category_link_sql.close()
wiki_category_link = wiki_category_link_re.findall(category_link)
category_link_size = len(wiki_category_link)
del wiki_category_link

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

        edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/"
        edge.startNodeID.primaryKeyInDomain = cat_title
        edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/"
        edge.endNodeID.primaryKeyInDomain = page_title
    if item.group(7)[1:-1] == 'subcat':
        cat_id = int(item.group(1))
        subcat_title = item.group(3)[1:-1]
        cat_title = item.group(2)[1:-1]
        edge.props.type = "HasSubset"

        edge.startNodeID.domain = "https://zh.wikipedia.org/wiki/"
        edge.startNodeID.primaryKeyInDomain = cat_title
        edge.endNodeID.domain = "https://zh.wikipedia.org/wiki/"
        edge.endNodeID.primaryKeyInDomain = subcat_title

        edge.subType = graphUpload_pb2.EdgeSubType.Value('PASS_REF')
    graph_upload_request.uploadTag = "testUpload"
    graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    response = gftIO.upload_graph(graph_upload_request, test_url,
                                  test_user_name, test_pwd)
    # print(item.group())
    if not response.failedEdges[0].error:
        print(response)
# for i in tqdm(range(0, len(wiki_category_link), batch_size)):
#     # for i in tqdm(range(0, 4)):
#     re_batch = {}
#     for j in range(batch_size):
#         re_batch[j] = re.search(source, last_span)
#         if re_batch[j] is not None:
#             last_span = re_batch[j].span()[1]
#             func(re_batch)

graph_upload_request = graphUpload_pb2.GraphUploadRequest()

# The first node
node = graph_upload_request.graph.nodes.add()

node.props.type = "OSet"

p1 = node.props.props.entries.add()
p1.key = "_body"
p1.value = "body of the first node"
p2 = node.props.props.entries.add()
p2.key = "_url"
p2.value = "http://dummy/"

node.businessID.domain = "https://zh.wikipedia.org/wiki/"
node.businessID.primaryKeyInDomain = '旧金山巨人队球员'

node.names.chinese = "中文名称"
node.names.english = "English Name"

# The second node
node = graph_upload_request.graph.nodes.add()

node.props.type = "i"

p1 = node.props.props.entries.add()
p1.key = "_body"
p1.value = "body of the second node"
p2 = node.props.props.entries.add()
p2.key = "_url"
p2.value = "http://dummy2/"

node.businessID.domain = "domain1"
node.businessID.primaryKeyInDomain = "word2"

node.names.chinese = "中文名称2"
node.names.english = "English Name2"

node.binaryContent = bytes("Binary Content", "utf-8")

# edge from the first node to the second node
edge = graph_upload_request.graph.edges.add()

edge.props.type = "DATAFLOW"

edge.startNodeID.domain = "domain1"
edge.startNodeID.primaryKeyInDomain = "word1"
edge.endNodeID.domain = "domain1"
edge.endNodeID.primaryKeyInDomain = "word2"

edge.subType = graphUpload_pb2.EdgeSubType.Value('PASS_REF')

# The second edge is incorrect.
edge = graph_upload_request.graph.edges.add()

edge.props.type = "DATAFLOW"

edge.startNodeID.domain = "domain1"
edge.startNodeID.primaryKeyInDomain = "word1"
edge.endNodeID.domain = "domain1"
edge.endNodeID.primaryKeyInDomain = "word3"

edge.subType = graphUpload_pb2.EdgeSubType.Value('PASS_REF')

# other information of the upload request
graph_upload_request.uploadTag = "testUpload"
graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
    'UPDATE')
graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
    'UPDATE')

response = gftIO.upload_graph(graph_upload_request, test_url, test_user_name,
                              test_pwd)
pk_str = "https://zh.wikipedia.org/wiki/Category:" + '/' + '社会哲学'
pk_md5 = hashlib.md5(pk_str.encode('utf-8')).hexdigest().upper()
print(pk_md5)
