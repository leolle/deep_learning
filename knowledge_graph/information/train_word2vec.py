#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch all the page from field csv files, pack them to a file.
fetch skill gid and extract page.
python wiki_preprocess.py > zh.wiki.docs
"""
import pandas as pd
import datetime
import gensim
import logging
import multiprocessing
import os
import re
import sys
from time import time, sleep
from timeit import default_timer
from gensim.models.word2vec import LineSentence
import codecs
import itertools
import string
from sys import stdin
from gensim import utils
from tqdm import tqdm
from gensim.models import KeyedVectors
import jieba
from fetch import extract_pages
from ylib import ylog
from preprocessing import complete_dir_path
from lib.gftTools import gftIO

# test fetch graph
prod_url = 'http://q.gftchina.com:13567'
test_user_name = 'wuwei'
test_pwd = 'gft'
gs_call = gftIO.GSCall(prod_url, test_user_name, test_pwd)


def skill_extraction(skill_gid, key, key_string, target_key, gs_call):
    """ extract skill
    Keyword Arguments:
    skill_gid  --
    key        -- source key
    key_string -- source key value
    target_key -- target key
    """
    graph = gs_call.get_graph_from_neo4j(skill_gid)
    ls_extract = []
    for g in graph.graphs:
        dict_node = {}
        for i in g.graph.nodes:
            # print(i.node_prop.props.entries)
            for e in i.node_prop.props.entries:
                dict_node[e.key] = e.value
                # print(dict_node)
            if dict_node[key] == key_string:
                ls_extract.append(dict_node[target_key])
    return ls_extract


if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #     print("Please use python wiki_preprocess.py output_path")
    #     exit()
    #    output_path = sys.argv[1]
    ylog.set_level(logging.DEBUG)
    ylog.console_on()
    ylog.filelog_on("wiki_upload")
    ylog.info("start")
    begin = time()
    user_path = os.path.expanduser("~")
    cat_path = user_path + '/share/deep_learning/data/GID/cat.txt'
    page_path = user_path + "/share/deep_learning/data/GID/page.txt"
    page_gid_file = open(page_path)
    lines = page_gid_file.read().splitlines()
    # page_gid = [s.strip() for s in lines]
    page_gid = skill_extraction('A0F920E1D1DB9E6EFD378FD1B9200461', '_type',
                                'readonlyDoc', '_gid', gs_call)
    output_path = sys.argv[1]

    extract_pages(page_gid, gs_call)
    model = gensim.models.Word2Vec(
        LineSentence('/tmp/test.txt'),
        size=200,
        window=5,
        min_count=2,
        workers=multiprocessing.cpu_count())
    model.wv.save_word2vec_format(
        complete_dir_path(output_path) + "wiki.w2v_org",
        complete_dir_path(output_path) + "wiki.vocab",
        binary=False)
    end = time()
    load_duration = end - begin
    logging.info("Total procesing time: %d seconds" % (end - begin))
