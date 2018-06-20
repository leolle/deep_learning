#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch skill gid and extract page.
preprocess text, remove punctuation, remove stopwords, tokenize.
train word2vec model.
save model.
"""
import gensim
import logging
import multiprocessing
import os
import sys
from time import time
from gensim.models.word2vec import LineSentence
# from ylib import ylog
from lib.gftTools import gftIO
from lib.gftTools.word2Vec import preprocessing
from google.protobuf.message import DecodeError
from lib.gftTools.graph_upload import batch_upload, upload_node
import re
from gensim.models import KeyedVectors
import pandas as pd
import copy

# test fetch graph
prod_url = 'http://172.16.103.106:9080'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)


def complete_dir_path(dir_path):
    if not os.path.exists(dir_path):
        os.mkdir(dir_path)
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


def extract_pages(gid, gs_call):
    """ Extract nodes read only documents from input list of gid or dataframe,
    preprocess text, remove punctuation, remove stopwords, tokenize, and save
    text to a tmp txt file.
    """
    from tempfile import gettempdir
    tmp_dir = gettempdir()
    output = open(tmp_dir + '/test.txt', 'wb')
    logging.info("extract pages")
    if isinstance(gid, list):
        for page_id in gid:
            #logging.info(page_id)
            try:
                text = gs_call.get_nodes_binary_data([page_id])
            except DecodeError:
                continue
            page = text.entries[0].data.data.decode('utf-8')
            text = preprocessing.preprocess_string(page)
            # ylog.debug(text)
            output.write(text.encode('utf-8'))
            output.write('\n'.encode('utf-8'))
    elif isinstance(gid, gftIO.GftTable):
        df_text = gid.as_mutable_column_tab()
        for item in df_text.iterrows():
            #logging.info(item[0])
            page = item[1]['Conclusion']
            try:
                text = preprocessing.preprocess_string(page)
            # ylog.debug(text)
            except:
                continue
            output.write(text.encode('utf-8'))
            output.write('\n'.encode('utf-8'))
    elif isinstance(gid, pd.DataFrame):
        df_text = copy.copy(gid)
        for item in df_text.iterrows():
            #logging.info(item[0])
            page = item[1]['Conclusion']
            try:
                text = preprocessing.preprocess_string(page)
            # ylog.debug(text)
            except:
                continue
            output.write(text.encode('utf-8'))
            output.write('\n'.encode('utf-8'))
    output.close()


def train_word2vec(gid):
    """
    extract page from gid, preprocessing text and train.

    Return:
    word2vec model
    """

    logging.basicConfig(
        format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)
    logging.info("start training")
    # model = KeyedVectors.load_word2vec_format('./analyst_report.w2v_org', binary=False)
    extract_pages(gid, gs_call)
    from tempfile import gettempdir
    tmp_dir = gettempdir()
    txt_path = tmp_dir + '/test.txt'
    model = gensim.models.Word2Vec(
        LineSentence(txt_path),
        size=200,
        window=5,
        min_count=5,
        workers=multiprocessing.cpu_count())
    #vocab_path = tmp_dir + '/vocab.txt'
    #with open(vocab_path, 'w') as f:
    #    f.write(str(model.vocab.keys()))
    #dict_key_re = re.compile("'[\u4e00-\u9fa5A-Za-z]+'")
    #uploaded_number = batch_upload(
    #    dict_key_re,
    #    vocab_path,
    #    200,
    #    upload_node,
    #    start=0,
    #    end=6080000000)
    # gftsave(gid='E43FEADC36DD7511A35D4AE6ADCB2CB4',model)
    return model.wv
