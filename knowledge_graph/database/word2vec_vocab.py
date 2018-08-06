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
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
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
    # model_path = user_path + \
    #     '/share/deep_learning/data/model/phrase/zhwiki/word2vec_org_whole_wiki_corpus_user_dict_m5'
    model_path = '~/share/deep_learning/data/model/analyst_report.w2v_org'
    # # open category sql file
    ylog.debug("reading model file")
    model = KeyedVectors.load_word2vec_format(model_path, binary=False)
    vocab_path = '/tmp/vocab.txt'
    dict_key_re = re.compile("'[\u4e00-\u9fa5A-Za-z]+'")
    print("writing nodes to local file")
    # writing
    with open('/tmp/vocab.txt', 'w') as f:
        f.write(str(model.vocab.keys()))
    ylog.debug("upload nodes to neo4j")
    # uploaded_number = batch_upload(
    #     dict_key_re,
    #     vocab_path,
    #     batch_size,
    #     upload_node,
    #     start=0,
    #     end=6080000000)

# print("uploaded number: %s" % (uploaded_number))
# with open(vocab_path, 'rb') as f:
#     for i, line in enumerate(tqdm(f)):
#         line_start_position = 0
#         line_end_position = len(line)
#         test_string = line[line_start_position:].decode('utf-8')
#         line_size = len(dict_key_re.findall(test_string))
#         for _ in range(0, line_size, batch_size):
#             # pause if find a file naed pause at the currend dir
#             re_batch = {}
#             last_span = dict_key_re.search(test_string).span()[0]

#             for j in range(batch_size):
#                 re_batch[j] = dict_key_re.search(test_string, last_span)
#                 if re_batch[j] is not None:
#                     last_span = re_batch[j].span()[1]
#                 print(re_batch[j].group())
#                 # uploaded_count = func(re_batch)
