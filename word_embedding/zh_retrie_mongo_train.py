#!/usr/bin/env python
# -*- coding: utf-8 -*-
# https://rare-technologies.com/data-streaming-in-python-generators-iterators-iterables/
import jieba
from jieba import analyse
import pymongo
import pandas as pd
from pymongo import MongoClient
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
from nltk.corpus import wordnet
import codecs
import itertools

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
        '/home/weiwu/share/deep_learning/data/zhwiki_categories/'):
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

    def __init__(self, common_terms, max_sentence_length):
        self.page_num = 0
        self.load_start = default_timer()
        self.stopwords = common_terms
        self.max_sentence_length = max_sentence_length

    def __iter__(self):
        for page_id in ls_pageid:
            try:
                # print(collection.find_one({"page_id": page_id})['title'])
                article = collection.find_one({"page_id": page_id})
                page = article['text']
                # sentences = page.splitlines()
                # sentence_stream = [
                #     parse_sent(doc) for doc in sentences if len(doc) > 1
                # ]
                # doc = list(itertools.chain.from_iterable(sentence_stream))
                tokenized_line = jieba.cut(filterpunt(page))
                doc = [word for word in tokenized_line]
                yield doc
                # for sent in sentence_stream:
                #     if len(sent) > 1:
                #         yield sent
            except TypeError:
                continue
            else:
                self.page_num = self.page_num + 1
        load_duration = default_timer() - self.load_start
        extract_rate = self.page_num / load_duration
        logging.info(
            "Finished %d-process extraction of %d articles in %.1fs (%.1f art/s)",
            process_count, self.page_num, load_duration, extract_rate)


if __name__ == '__main__':

    if len(sys.argv) != 2:
        print("Please use python train_with_gensim.py output_path")
        exit()
    output_path = sys.argv[1]
    begin = time()

    pages = MySentences(stopwords)
    model = gensim.models.Word2Vec(
        pages,
        size=200,
        window=10,
        min_count=10,
        workers=multiprocessing.cpu_count())
    model.save(complete_dir_path(output_path) + "word2vec_gensim")
    model.wv.save_word2vec_format(
        complete_dir_path(output_path) + "word2vec_org",
        complete_dir_path(output_path) + "vocabulary",
        binary=False)

    end = time()
    print("Total procesing time: %d seconds" % (end - begin))

# page = collection.find_one({"page_id": 2763})['text']
# sent_list = page.splitlines()
# sentence_stream = [parse_sent(doc) for doc in sent_list if len(doc) > 1]
# from gensim.models import KeyedVectors
# zh_model_path = '/home/weiwu/share/deep_learning/data/model/phrase/zhwiki/word2vec_org'
# zh_model = KeyedVectors.load_word2vec_format(zh_model_path)

# result = zh_model.most_similar(u"计算机", topn=10)
# for e in result:
#     print e[0], e[1]

# zh_model.similarity(u'日本', u'微软')

str_in = "机器学习是一门研究在非特定编程条件下让计算机采取行动的学科。最近二十年，机器学习为我们带来了自动驾驶汽车、实用的语音识别、高效的网络搜索，让我们对人类基因的解读能力大大提高。当今机器学习技术已经非常普遍，您很可能在毫无察觉情况下每天使用几十次。许多研究者还认为机器学习是人工智能（AI）取得进展的最有效途径。在本课程中，您将学习最高效的机器学习技术，了解如何使用这些技术，并自己动手实践这些技术。更重要的是，您将不仅将学习理论知识，还将学习如何实践，如何快速使用强大的技术来解决新问题。最后，您将了解在硅谷企业如何在机器学习和AI领域进行创新。 本课程将广泛介绍机器学习、数据挖掘和统计模式识别。相关主题包括：(i) 监督式学习（参数和非参数算法、支持向量机、核函数和神经网络）。(ii) 无监督学习（集群、降维、推荐系统和深度学习）。(iii) 机器学习实例（偏见/方差理论；机器学习和AI领域的创新）。课程将引用很多案例和应用，您还需要学习如何在不同领域应用学习算法，例如智能机器人（感知和控制）、文本理解（网络搜索和垃圾邮件过滤）、计算机视觉、医学信息学、音频、数据库挖掘等领域。"
seg_list = jieba.cut(str_in)
text = " ".join(seg_list)
sentences = list(
    word for word in jieba.cut(str_in, HMM=True)
    if word not in stopwords and len(word.strip()) > 1)
model_test = gensim.models.Word2Vec(
    sentences, size=100, window=5, min_count=2, workers=2)
print(" / ".join(
    list(
        word for word in jieba.cut(str_in, HMM=True)
        if word not in stopwords and len(word.strip()) > 1)))
result = model_test.most_similar(u"女", topn=10)
for e in result:
    print e[0], e[1]

for v in model_test.wv.vocab:
    print v

# seg_list = [parse_sent(word) for word in jieba.cut(str_in, HMM=True)]
# for x in seg_list:
#     if len(x) > 0:
#         print x[0]

# for x in seg_list:
#     print('/')
#     print x
from gensim.models.word2vec import LineSentence
zh_wiki_corpus = '/home/weiwu/share/deep_learning/data/wiki.zh.text.simple.clean.seg'
sentences = LineSentence(zh_wiki_corpus)
sent_iter = iter(sentences)
sample = next(sent_iter)

article = collection.find_one({"page_id": 595})
page = article['text']
print page

# remove whitespace at the beginning
tokenized_line = jieba.cut(filterpunt(page))
doc = [word for word in tokenized_line]
# parse digits, remove signs
is_alpha_word_line = [
    word for word in tokenized_line
    if not wordnet.synsets(word) and not word.isdigit()
    if word not in stopwords and len(word.strip()) > 1
]
