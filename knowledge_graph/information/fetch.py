# -*- coding: utf-8 -*-
import time
import re
from lib.gftTools import gftIO
from lib.gftTools.proto import graphUpload_pb2
from tqdm import tqdm
import random
from ylib import ylog
import logging
import os, sys
import hashlib
from google.protobuf.message import EncodeError
from urllib.error import HTTPError
from lib.gftTools.gftIO import GSError
from pymongo import MongoClient
from google.protobuf.message import DecodeError
from hanziconv import HanziConv
import json
import logging
# from gensim.parsing import preprocessing
from gensim import utils
from preprocessing import preprocess_string
from preprocessing import strip_numeric, remove_stopwords, strip_punctuation, tokenize
user_path = os.path.expanduser("~")

# ylog.debug(page_gid)
# test fetch graph
test_url = 'http://192.168.1.166:9080'
prod_url = 'http://q.gftchina.com:13567'
test_user_name = 'wuwei'
test_pwd = 'gft'


def extract_pages(ls_pageid, gs_call):
    from tempfile import gettempdir
    tmp_dir = gettempdir()
    output = open(tmp_dir + '/test.txt', 'w')
    for page_id in ls_pageid:
        ylog.debug(page_id)
        try:
            text = gs_call.get_nodes_binary_data([page_id])
        except DecodeError:
            continue
        page = text.entries[0].data.data.decode('utf-8')
        text = preprocess_string(page)
        # ylog.debug(text)
        output.write(text + '\n')
    output.close()


if __name__ == '__main__':
    ylog.set_level(logging.DEBUG)
    ylog.console_on()
    ylog.filelog_on("wiki_upload")
    gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)
    cat_path = user_path + '/share/deep_learning/data/GID/cat.txt'
    page_path = user_path + "/share/deep_learning/data/GID/page.txt"
    page_gid_file = open(page_path)
    lines = page_gid_file.read().splitlines()
    page_gid = [s.strip() for s in lines]
    for gid in page_gid:
        ylog.debug(gid)
        extract_pages(gid, gs_call)
