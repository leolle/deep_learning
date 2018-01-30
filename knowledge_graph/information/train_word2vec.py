#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch all the page from field csv files, pack them to a file.
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
    page_gid = [s.strip() for s in lines]
    output_path = sys.argv[1]

    for gid in page_gid:
        ylog.debug(gid)
        extract_pages(gid)
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
