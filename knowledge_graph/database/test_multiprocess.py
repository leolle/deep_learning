# -*- coding: utf-8 -*-
import os, sys
import logging
from ylib import ylog
ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("wiki_upload")
import re
from lib.gftTools import gftIO
# import skill_pb2
import graphUpload_pb2
from tqdm import tqdm
import time
import hashlib
from graph_upload import batch_upload
from graph_upload import upload_cat_node
from graph_upload import upload_page_node
from graph_upload import upload_edge
from graph_upload import delete_edge

# ylog.debug("test")
batch_size = 2
# test fetch graph
test_url = 'http://192.168.1.166:9080'
test_user_name = 'wuwei'
test_pwd = 'gft'

ylog.debug('reading sql files')
category_link_path = './zhwiki-latest-categorylinks.zhs.sql'
wiki_category_link_re = re.compile(
    "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
)
wiki_category_link_size = 12
n = 4
chunks = wiki_category_link_size / n
chunk_num = 5
start = chunk_num * chunks
end = (chunk_num + 1) * chunks
# category_link_path = './zhwiki-latest-categorylinks.zhs.sql'
# category_link_sql = open(category_link_path, 'r')
# category_link = category_link_sql.read()
# category_link_sql.close()
# uploaded_number = batch_upload(wiki_category_link_re, category_link,
#                                wiki_category_link_size, batch_size, upload_edge)

with open(category_link_path, 'r') as f:
    for i, category_link in enumerate(f):
        # print("uploading wiki categories")
        # uploaded_number = batch_upload(wiki_category_link_re, category_link,
        #                                wiki_category_link_size, batch_size,
        #                                delete_edge)
        # print("uploaded number: %s, actual number in wiki: %s" %
        #       (uploaded_number, wiki_category_link_size))
        if i >= start and i <= end:
            print("line #: %s" % i)
            try:
                last_span = wiki_category_link_re.search(category_link).span()[
                    0]
            except AttributeError:
                continue

            print(category_link)
            wiki_category_link_line_size = len(
                wiki_category_link_re.findall(category_link))
            for i in range(0, wiki_category_link_line_size, batch_size):
                re_batch = {}
                for j in range(batch_size):
                    re_batch[j] = wiki_category_link_re.search(
                        category_link, last_span)
                    if re_batch[j] is not None:
                        last_span = re_batch[j].span()[1]
        elif i > end:
            break
            # print(re_batch)
        #        print(re_batch[j])
