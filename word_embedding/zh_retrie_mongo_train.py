# encoding: utf-8
import jieba
from jieba import analyse
import pymongo
import pandas as pd
from pymongo import MongoClient
import datetime
import pprint
from urllib import quote_plus
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
        '/home/weiwu/share/deep_learning/data/zhwiki_categories_test/'):
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

    def __iter__(self):
        for page_id in ls_pageid:
            try:
                # print(collection.find_one({"page_id": page_id})['title'])
                article = collection.find_one({"page_id": page_id})
                page = article['text']
                sentences = page.splitlines()
                sentence_stream = [
                    parse_sent(doc) for doc in sentences if len(doc) > 1
                ]
                for sent in sentence_stream:
                    if len(sent) > 1:
                        yield sent
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

# result = model.most_similar(u"足球")
# for e in result:
#     print e[0], e[1]
str_in = "小明硕士毕业于中国科学院计算所，后在日本京都大学深造，凭借过人天赋，旁人若在另一方面爱他，他每即躲开。"
seg_list = jieba.cut(str_in)
text = " ".join(seg_list)
print(" / ".join(
    list(
        word for word in jieba.cut(str_in, HMM=True)
        if word not in stopwords and len(word.strip()) > 1)))

seg_list = [parse_sent(word) for word in jieba.cut(str_in, HMM=True)]
for x in seg_list:
    if len(x) > 0:
        print x[0]

for x in seg_list:
    print('/')
    print x
