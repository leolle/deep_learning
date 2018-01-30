# -*- coding: utf-8 -*-
from ylib import ylog
import re
from lib.gftTools import gftIO
import os
import sys
from google.protobuf.message import EncodeError
from google.protobuf.message import DecodeError
from urllib.error import HTTPError
from urllib.error import URLError
from pymongo import MongoClient
from graph_upload import batch_upload, upload_edge, upload_cat_node, upload_page_node, delete_edge
client = MongoClient('mongodb://localhost:27017/')
db = client['wiki']
collection = db.zhwiki
batch_size = 20
# links number
# wiki_category_link line size = 1503
# wiki_category_link_size = 8
n = 4
# chunks = int(wiki_category_link_size / n)
# Maximum number of times to retry before giving up.
MAX_RETRIES = 10
NODES_FAIL_MAX_RETRIES = 3
# Always retry when these exceptions are raised.
RETRIABLE_EXCEPTIONS = (EncodeError, DecodeError, HTTPError)
# Always retry when an apiclient.errors.HttpError with one of these status
# codes is raised.
RETRIABLE_STATUS_CODES = [500, 502, 503, 504, 111]
IGNORE_CATEGORIES = [
    '使用Catnav的页面', '缺少Wikidata链接的维基共享资源分类', '隐藏分类', '追踪分类', '维基百科特殊页面',
    '维基百科分类', '维基百科维护', '无需细分的分类', '不要删除的分类', '母分类', '全部重定向分类', '特殊条目'
]

# test fetch graph
test_url = 'http://192.168.1.166:9080'
# prod_url = 'http://q.gftchina.com:13567/vqservice/vq/'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(test_url, test_user_name, test_pwd)

if __name__ == '__main__':
    import logging
    ylog.set_level(logging.DEBUG)
    # ylog.console_on()
    ylog.filelog_on("wiki_upload")
    try:
        start_cat = int(sys.argv[1])
        start_page = int(sys.argv[2])
        start_edge = int(sys.argv[3])
    except:
        print(
            'try python main.py cat_start_line page_start_line link_start_line')
        start_cat = 0
        start_page = 0
        start_edge = 0
    user_path = os.path.expanduser("~")
    category_path = "./data/zhwiki-latest-category.zhs.sql"
    # open category sql file
    wiki_category_re = re.compile(
        "\(([0-9]+),('[^,]+'),([0-9]+),([0-9]+),([0-9]+)\)")
    print("uploading wiki categories")
    uploaded_number = batch_upload(
        wiki_category_re,
        category_path,
        batch_size,
        upload_cat_node,
        start=start_cat,
        end=68)
    print("uploaded number: %s" % (uploaded_number))

    # # open page sql file
    # page_path = "./data/zhwiki-latest-page.zhs.sql"
    # wiki_page_re = re.compile(
    #     "\(([0-9]+),([0-9]+),('[^,]+'),('[^,]+|'),([0-9]+),([0-9]+),([0-9]+),0.([0-9]+),('[^,]+'),('[^,]+'|NULL),([0-9]+),([0-9]+),('[^,]+'),([^,]+)\)"
    # )
    # print("uploading wiki page")
    # uploaded_number = batch_upload(
    #     wiki_page_re,
    #     page_path,
    #     batch_size,
    #     upload_page_node,
    #     start=start_page,
    #     end=660)
    # print("uploaded number: %s" % (uploaded_number))

    # # # upload edge

    # # chunk_num
    # # start = chunk_num * chunks
    # # end = (chunk_num + 1) * chunks
    # category_link_path = './data/zhwiki-latest-categorylinks.zhs.sql'
    # wiki_category_link_re = re.compile(
    #     "\(([0-9]+),('[^,]+'),('[^']+'),('\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}'),('[^']*'),('[^,]+'),('[^,]+')\)"
    # )

    # ylog.debug('reading link sql file')
    # ylog.debug("uploading wiki categorie page link")
    # uploaded_number = batch_upload(
    #     wiki_category_link_re,
    #     category_link_path,
    #     batch_size,
    #     upload_edge,
    #     start=start_edge,
    #     end=1000000000)
    # print("uploaded number: %s" % (uploaded_number))
