#!/usr/bin/env python
# -*- coding: utf-8 -*-
import jieba
from jieba import analyse
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

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
jieba.analyse.set_stop_words("stopwords")

punct = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')

filterpunt = lambda s: ''.join(filter(lambda x: x not in punct, s))
filterpuntl = lambda l: list(filter(lambda x: x not in punct, l))


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


pages_csv = pd.DataFrame()
for root, dirs, files in os.walk(
        '/home/oem/share/deep_learning/data/zhwiki_categories_test3/'):
    for filename in files:
        file_path = root + '/' + filename
        page_read = pd.read_csv(file_path)
        pages_csv = pd.concat([pages_csv, page_read])
ls_pageid = pages_csv.pageid.unique()

client = MongoClient('mongodb://localhost:27017/')
db = client['wiki']
collection = db.zhwiki
stopwords = codecs.open('stopwords', 'r', 'utf-8').read().split()

process_count = multiprocessing.cpu_count()


class MySentences(object):
    """lines -> sentence list(['...', '...',...]) ->
    words list([[[' '],[' ']],[[' '],[' ']],...) ->
    phrase([['a_b','c_d']])"""

    def __init__(self, common_terms):
        self.page_num = 0
        self.load_start = default_timer()
        self.stopwords = common_terms
        self.max_sentence_length = 10000

    def __iter__(self):
        logging.info('cpus %s' % multiprocessing.cpu_count())
        for page_id in ls_pageid:
            try:
                # print(collection.find_one({"page_id": page_id})['title'])
                article = collection.find_one({"page_id": page_id})
                page = article['text']
                title = article['title']
                self.page_num = self.page_num + 1
                if self.page_num % 100 == 0:
                    load_duration = default_timer() - self.load_start
                    print self.page_num / load_duration
            except TypeError:
                continue
            else:
                #print page_id
                # print title
                # sentences = page.splitlines()
                # sentence_stream = [
                #     parse_sent(doc) for doc in sentences if len(doc) > 1
                # ]
                # doc = list(itertools.chain.from_iterable(sentence_stream))
                tokenized_line = jieba.cut(filterpunt(page))
                doc = [word for word in tokenized_line]
                # yield title, doc
                i = 0
                while i < len(doc):
                    yield doc[i:i + self.max_sentence_length]
                    i += self.max_sentence_length
                #yield doc

        extract_rate = self.page_num / load_duration
        logging.info(
            "Finished %d-process extraction of %d articles in %.1fs (%.1f art/s)",
            process_count, self.page_num, load_duration, extract_rate)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please use python wiki_preprocess.py output_path")
        exit()
    output_path = sys.argv[1]
    begin = time()

    page_num = 0
    load_start = default_timer()
    printable = set(string.printable)
    output = open(output_path, 'w')
    for page_id in ls_pageid:
        try:
            # print(collection.find_one({"page_id": page_id})['title'])
            article = collection.find_one({"page_id": page_id})
            page = article['text']
            page_num = page_num + 1
            if page_num % 100 == 0:
                load_duration = default_timer() - load_start
                print("extract rate %s articles/second" %
                      (page_num / load_duration))
            lines = page.splitlines()
            new_doc = ''
            for line in lines:
                filter_line = filter(lambda x: x not in printable, line).strip()
                if filter_line != "":
                    new_doc.append(filter_line)
        except TypeError:
            continue
        else:
            output.write(" ".join(page) + '\n')
    output.close()
    end = time()
    print("Total procesing time: %d seconds" % (end - begin))
    extract_rate = page_num / load_duration
    logging.info(
        "Finished %d-process extraction of %d articles in %.1fs (%.1f art/s)",
        process_count, page_num, load_duration, extract_rate)

# result = model.most_similar(u"足球")
# for e in result:
#     print e[0], e[1]
