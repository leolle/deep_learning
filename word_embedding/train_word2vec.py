#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch all the page from field csv files, pack them to a file.
python wiki_preprocess.py > zh.wiki.docs
"""
import pandas as pd
from pymongo import MongoClient
import datetime
import gensim
import logging
import multiprocessing
import os
import sys
from time import time, sleep
from timeit import default_timer
from gensim.models.word2vec import LineSentence
import codecs
from tqdm import tqdm
from gensim.models import KeyedVectors
from ylib.preprocessing import preprocess_string

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

punctuation = u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…'''
STOPWORDS = codecs.open('stopwords', 'r', 'utf-8').read().split()

client = MongoClient('mongodb://localhost:27017/')
db = client['wiki']
collection = db.zhwiki
stopwords = codecs.open('stopwords', 'r', 'utf-8').read().split()

# article = collection.find_one({"page_id": 595})
# page = article['text']

# for token in tokens:
#     print token
# print remove_stopwords(page)

# print strip_punctuation(page)

# print strip_numeric(page)
# page = """人口密度
# 人口密度是指在一定时期一定单位面积土地上的平均人口数目，计算方式是其总人口数除以总面积。一般使用的单位是每平方公里人数或每平方米所居住的人口数。人口密度是反映人口分布疏密程度的常用数量指标。它通常用于计算一个国家、地区、城市或全球的人口分布状况。适当的人口密度能够保证良好的居住、卫生及经济条件。
# 以下为世界人口密度最高的10个国家或地区：
# 以下为世界人口密度最低的10个国家或地区：
# """
# print cut_article(page)
# print cut_paragraph(page)


def find_page_id(csv_path):
    pages_csv = pd.DataFrame()
    for root, dirs, files in os.walk(csv_path):
        for filename in files:
            file_path = root + '/' + filename
            page_read = pd.read_csv(file_path)
            pages_csv = pd.concat([pages_csv, page_read])
    ls_pageid = pages_csv.pageid.unique()
    return ls_pageid


def find_category_page(cat_path):
    """find categories page title and id
    """
    page_read = pd.read_csv(cat_path)
    ls_pageid = page_read.pageid.unique()
    return ls_pageid


def extract_pages(ls_pageid):
    str_paragraph = u''
    from tempfile import gettempdir
    tmp_dir = gettempdir()
    # output_path = sys.argv[2]
    output = open(tmp_dir + '/test.txt', 'w')
    for page_id in ls_pageid:
        try:
            article = collection.find_one({"page_id": page_id})
            page = article['text']
            text = preprocess_string(page)
            output.write(text.encode('utf-8') + '\n')
            # print text
        except TypeError:
            continue
    # return str_paragraph


# dir_path = '/home/weiwu/share/deep_learning/data/zhwiki_categories_test3/zh_finance_level_3.csv'
# ls_pageid = find_category_page(dir_path)
# extract_pages(ls_pageid)

# model = gensim.models.Word2Vec(
#     LineSentence(str_parag),
#     size=200,
#     window=5,
#     min_count=2,
#     workers=multiprocessing.cpu_count())

if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #     print("Please use python wiki_preprocess.py output_path")
    #     exit()
    #    output_path = sys.argv[1]
    logging.info("start")
    begin = time()

    dir_path = sys.argv[1]
    output_path = sys.argv[2]

    for root, dirs, files in os.walk(dir_path):
        for filename in files:
            file_path = root + '/' + filename
            logging.info(filename)
            ls_pageid = find_category_page(file_path)
            if len(ls_pageid) == 0:
                continue
            # ls_pg_text_clean = extract_pages(ls_pageid)
            extract_pages(ls_pageid)
            model = gensim.models.Word2Vec(
                LineSentence('/tmp/test.txt'),
                size=200,
                window=5,
                min_count=2,
                workers=multiprocessing.cpu_count())
            model.wv.save_word2vec_format(
                complete_dir_path(output_path) + filename[:-4] + ".w2v_org",
                complete_dir_path(output_path) + filename[:-4] + ".vocab",
                binary=False)
    end = time()
    load_duration = end - begin
    logging.info("Total procesing time: %d seconds" % (end - begin))
