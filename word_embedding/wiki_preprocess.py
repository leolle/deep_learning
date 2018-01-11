#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
fetch all the page from field csv files, pack them to a file.
python wiki_preprocess.py > zh.wiki.docs
"""
import pymongo
import pandas as pd
from pymongo import MongoClient
import datetime
import pprint
import gensim
import logging
import multiprocessing
import os
import re
import sys
from time import time, sleep
from timeit import default_timer
from gensim.models.word2vec import LineSentence
from nltk.corpus import wordnet
import codecs
import itertools
import string
from sys import stdin
from gensim.parsing import preprocessing
from gensim import utils
import glob
from tqdm import tqdm

import jieba
jieba.load_userdict("/home/oem/share/deep_learning/data/dict/jieba.txt")
from jieba import analyse
jieba.analyse.set_stop_words("stopwords")

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
punct = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')
punctuation = u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻︽︿﹁﹃﹙﹛﹝（｛“‘-—_…'''
filterpunt = lambda s: ''.join(filter(lambda x: x not in punct, s))
filterpuntl = lambda l: list(filter(lambda x: x not in punct, l))
STOPWORDS = codecs.open('stopwords', 'r', 'utf-8').read().split()


def complete_dir_path(dir_path):
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


def parse_sent(sentence):
    """parse sentence to list of words
    """
    # remove whitespace at the beginning
    sline = sentence.strip()
    tokenized_line = jieba.cut(filterpunt(sline))
    # parse digits, remove signs
    is_alpha_word_line = [
        word for word in tokenized_line
        if not wordnet.synsets(word) and not word.isdigit()
        if word not in stopwords and len(word.strip()) > 1
    ]

    return is_alpha_word_line


def find_page_id(csv_path):
    pages_csv = pd.DataFrame()
    for root, dirs, files in os.walk(csv_path):
        for filename in files:
            file_path = root + '/' + filename
            page_read = pd.read_csv(file_path)
            pages_csv = pd.concat([pages_csv, page_read])
    ls_pageid = pages_csv.pageid.unique()
    return ls_pageid


RE_PUNCT = re.compile(r'([%s])+' % re.escape(punctuation + string.punctuation),
                      re.UNICODE)
RE_TAGS = re.compile(r"<([^>]+)>", re.UNICODE)
RE_NUMERIC = re.compile(r"[0-9]+", re.UNICODE)
RE_NONALPHA = re.compile(r"\W", re.UNICODE)
RE_WHITESPACE = re.compile(r"(\s)+", re.UNICODE)


def remove_stopwords(s):
    """Remove :STOPWORDS from `s`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode string without :STOPWORDS.

    EXAMPLES
    --------
    >>> from gensim.parsing.preprocessing import remove_stopwords
    >>> remove_stopwords(u"一般使用的单位是每平方公里人数或每平方米所居住的人口数。")
    u'使用单位平方公里人数每平方米居住人口数。'

    """
    s = utils.to_unicode(s)
    tokens_generator = jieba.cut(s)
    return "".join(w for w in tokens_generator if w not in STOPWORDS)


def strip_punctuation(s):
    """Replace punctuation characters with spaces in `s` using :const:`RE_PUNCT`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode string without punctuation characters.

    Examples
    --------
    >>> from wiki_preprocess import strip_punctuation
    >>> strip_punctuation("通常用于计算一个国家、地区、城市全球人口分布状况。")
    u'它通常用于计算一个国家 地区 城市或全球的人口分布状况 '
    >>> strip_punctuation("A semicolon is a stronger break than a comma, but not as much as a full stop!")
    u'A semicolon is a stronger break than a comma  but not as much as a full stop '
    """
    s = utils.to_unicode(s)
    return RE_PUNCT.sub(" ", s)


def strip_numeric(s):
    """Remove digits from `s` using :const:`RE_NUMERIC`.

    Parameters
    ----------
    s : str

    Returns
    -------
    str
        Unicode  string without digits.

    Examples
    --------
    >>> from wiki_preprocess import strip_numeric
    >>> strip_numeric("0text24gensim365test")
    u'textgensimtest'
    >>> strip_numeric(u"原子核(atomic nucleus)，占了99.96%以上原子的质量。它的直径在10-12至10-13公分之间,1912年")
    u"原子核(atomic nucleus)，占了.%以上原子的质量。它的直径在-至-公分之间,年"
    """
    s = utils.to_unicode(s)
    # tokens_generator = jieba.cut(s)
    # return "".join(w for w in tokens_generator if w not in STOPWORDS)
    return RE_NUMERIC.sub("", s)


def cut_paragraph(s):
    """cut pages to paragraph.
    Keyword Arguments:
    s -- string
    """
    s = utils.to_unicode(s)
    return '\n'.join(s.split())


def cut_article(s):
    """join pages to a whole document.
    Keyword Arguments:
    s -- string
    """
    s = utils.to_unicode(s)
    return ''.join(s.split())


client = MongoClient('mongodb://localhost:27017/')
db = client['wiki']
collection = db.zhwiki
stopwords = codecs.open('stopwords', 'r', 'utf-8').read().split()

process_count = multiprocessing.cpu_count()

article = collection.find_one({"page_id": 595})
page = article['text']

filterpunt_text = filterpunt(page)
tokens_generator = jieba.cut(filterpunt_text)
tokens = [x for x in tokens_generator if not x.isspace()]

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
DEFAULT_FILTERS = [
    cut_article, strip_numeric, remove_stopwords, strip_punctuation
]


def preprocess_string(s, filters=DEFAULT_FILTERS):
    """Apply list of chosen filters to `s`.

    Default list of filters:

    * :func:`preprocessing.strip_punctuation`,
    * :func:`preprocessing.strip_numeric`,
    * :func:`preprocessing.remove_stopwords`,

    Parameters
    ----------
    s : str
    filters: list of functions, optional

    Returns
    -------
    list of str
        Processed strings (cleaned).

    Examples
    --------
    >>> preprocessing import preprocess_string
    >>> preprocess_string("<i>Hel 9lo</i> <b>Wo9 rld</b>! Th3     weather_is really g00d today, isn't it?")
    [u'hel', u'rld', u'weather', u'todai', u'isn']
    >>>
    >>> s = "<i>Hel 9lo</i> <b>Wo9 rld</b>! Th3     weather_is really g00d today, isn't it?"
    >>> CUSTOM_FILTERS = [lambda x: x.lower(), strip_tags, strip_punctuation]
    >>> preprocess_string(s, CUSTOM_FILTERS)
    [u'hel', u'9lo', u'wo9', u'rld', u'th3', u'weather', u'is', u'really', u'g00d', u'today', u'isn', u't', u'it']

    """
    s = utils.to_unicode(s)
    for f in filters:
        s = f(s)
    return s


# print(preprocess_string(page))

if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #     print("Please use python wiki_preprocess.py output_path")
    #     exit()
    #    output_path = sys.argv[1]
    logging.info("start")
    begin = time()

    page_num = 0
    load_start = default_timer()
    printable = set(string.printable)
    ls_pageid = find_page_id(sys.argv[1])
    output_path = sys.argv[2]
    output = open(output_path, 'w')
    for page_id in tqdm(ls_pageid):
        try:
            article = collection.find_one({"page_id": page_id})
            # logging.info(article['title'])
            page = article['text']
            page_num = page_num + 1
            if page_num % 100 == 0:
                load_duration = default_timer() - load_start
                logging.info("extract rate %s articles/second" %
                             (page_num / load_duration))
            # print(preprocess_string(page))
            #             output.write(preprocess_string(page) + "\n")
            text = preprocess_string(page)
            output.write(text.encode('utf-8') + '\n')
        except TypeError:
            continue
    output.close()
    end = time()
    load_duration = end - begin
    logging.info("Total procesing time: %d seconds" % (end - begin))
    extract_rate = page_num / load_duration
    logging.info(
        "Finished %d-process extraction of %d articles in %.1fs (%.1f art/s)",
        process_count, page_num, load_duration, extract_rate)
