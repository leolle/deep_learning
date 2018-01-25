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
wiki_category_size = len(wiki_category_re.findall(category))

# TODO: add counter of successful uploaded edges.
ylog.debug('start uploading edges')
last_span = wiki_category_re.search(category).span()[0]
