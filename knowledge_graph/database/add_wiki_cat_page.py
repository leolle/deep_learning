# -*- coding: utf-8 -*-
import pandas as pd
import numpy as np
from datetime import datetime
import re
from lib.gftTools import gftIO
import skill_pb2
import graphUpload_pb2
from tqdm import tqdm

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

category_path = "/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-category.zhs.sql"
category_link_path = '/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-categorylinks.zhs.sql'
page_path = "/home/weiwu/share/deep_learning/data/zhwiki_cat_pg_lk/zhwiki-latest-page.zhs.sql"
category_sql = open(category_path, 'r')
category = category_sql.read()
category_sql.close()
# category_link_sql = open(category_link_path, 'r')
# category_link = category_link_sql.read()
# category_link_sql.close()
wiki_category_re = re.compile(
    "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
wiki_category = re.findall(wiki_category_re, category)
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^,]+'),('[^,]+'),('[^,]+|'),('[^,]+'),('[^,]+')\)")

##wiki_category_link = re.findall(wiki_category_re, category)
# edge = wiki_category_link_re.search(category_link)


# wiki = wiki_content.search(lines)
# for i in range(len(all_matched_content)):
def upload_cat_node(re_match_object, foo):
    """ upload node created from regular expression matched object.
    ('5', "'科学小作品'", '104', '12', '0')
    Keyword Arguments:
    re_match_object -- re object
    f               -- local file to write
    """
    graph_upload_request = graphUpload_pb2.GraphUploadRequest()

    # The first node
    node = graph_upload_request.graph.nodes.add()

    node.props.type = "i"

    p0 = node.props.props.entries.add()
    p0.key = "cat_id"
    # print(re_match_object.group(1))
    p0.value = re_match_object.group(1)
    p1 = node.props.props.entries.add()
    p1.key = "cat_title"
    p1.value = re_match_object.group(2)
    p2 = node.props.props.entries.add()
    p2.key = "cat_pages"
    p2.value = re_match_object.group(3)
    p3 = node.props.props.entries.add()
    p3.key = "cat_subcats"
    p3.value = re_match_object.group(4)
    p4 = node.props.props.entries.add()
    p4.key = "cat_files"
    p4.value = re_match_object.group(5)

    node.businessID.domain = "https://en.wikipedia.org/wiki/"
    node.businessID.primaryKeyInDomain = p1.value

    node.names.chinese = p1.value
    # other information of the upload request
    graph_upload_request.uploadTag = "testUpload"
    graph_upload_request.nodeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')
    graph_upload_request.edgeAction4Duplication = graphUpload_pb2.Action4Duplication.Value(
        'UPDATE')

    response = gftIO.upload_graph(graph_upload_request, test_url,
                                  test_user_name, test_pwd)
    # foo.write(node.SerializeToString())

    return response


def upload_edge(re_match_object, f):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    f               -- local file to write
    """
    pass


def upload_page(re_match_object, f):
    """ upload edge created from regular expression matched object.
    (9,'En-3_使用者','MOUNTAIN','2015-09-02 13:44:06','','uppercase','page')
    Keyword Arguments:
    re_match_object -- re object
    f               -- local file to write
    """
    pass


batch_size = 3
# global last_span
last_span = wiki_category_re.search(category).span()[1]
# re_batch = {}
from pprint import pprint
#def chunks(last_span=last_span):
for i in range(0, len(category), batch_size):
    re_batch = {}
    for j in range(batch_size):
        re_batch[j] = wiki_category_re.search(category, last_span)
        if re_batch[j] is not None:
            last_span = re_batch[j].span()[1]
    # pprint(re_batch)

for i in tqdm(range(len(wiki_category))):
    with open('wiki.proto', "wb") as f:
        if i == 0:
            content = wiki_category_re.search(category)
            span = content.span()
            # print(content.group(0))
            res = upload_cat_node(content, f)
        else:
            content = wiki_category_re.search(category, span[1])
            span = content.span()
            # print(content.group(0))
            res = upload_cat_node(content, f)

# Write the new address book back to disk.
# with open('wiki.proto', "wb") as f:
#    f.write(wiki_node.SerializeToString())

groups = re.findall("\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)",
                    category)
# # In[80]: len(groups)
# # Out[81]: 381500
# # graph_upload_request = graphUpload_pb2.GraphUploadRequest()
wiki = graphUpload_pb2.NodeInfo()
with open('./wiki.proto', "rb") as f:
    wiki.ParseFromString(f.read())


# Iterates though all categories in the wiki graph and prints info about them.
def ListWikiCat(wiki_cat):
    for cat in wiki_cat.graph.nodes:
        print("Person ID:", cat.p1)
        # print("  Name:", person.name)
        # if person.email != "":
        #     print("  E-mail address:", person.email)

        # for phone_number in person.phones:
        #     if phone_number.type == addressbook_pb2.Person.MOBILE:
        #         print("  Mobile phone #:", end=" ")
        #     elif phone_number.type == addressbook_pb2.Person.HOME:
        #         print("  Home phone #:", end=" ")
        #     elif phone_number.type == addressbook_pb2.Person.WORK:
        #         print("  Work phone #:", end=" ")
        #     print(phone_number.number)


# ListWikiCat(wiki)
