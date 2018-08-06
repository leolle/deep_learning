# -*- coding: utf-8 -*-
"""
extract wiki categories from dump sql file, and then upload to neo4j.
"""
from ylib import ylog
import re
from lib.gftTools import gftIO
import os
import sys
from tqdm import tqdm
from google.protobuf.message import EncodeError
from google.protobuf.message import DecodeError
import pickle
from urllib.error import HTTPError
from urllib.error import URLError
from pymongo import MongoClient
from graph_upload import batch_upload, upload_edge, upload_cat_node, delete_edge, upload_edge_from_graph, upload_single_edge, upload_node
# how many nodes or edge to upload in a batch
batch_size = 200
# links number
# wiki_category_link line size = 1503
# wiki_category_link_size = 8
n = 4
### chunks = int(wiki_category_link_size / n)

# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
NODES_FAIL_MAX_RETRIES = 3

# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (EncodeError, DecodeError, HTTPError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504, 111]
# ignore those looped categories

# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)

if __name__ == '__main__':
    user_path = os.path.expanduser("~")
    import logging
    ylog.set_level(logging.DEBUG)
    ylog.console_on()
    ylog.filelog_on("wiki_upload")

    keywords_path = './data/keywords.txt'
    # open category sql file
    keywords_re = re.compile("'\S+'")
    print("uploading wiki categories")
    uploaded_number = batch_upload(
        keywords_re,
        keywords_path,
        batch_size,
        upload_node,
        start=0,
        end=6080000000)
    print("uploaded number: %s" % (uploaded_number))
