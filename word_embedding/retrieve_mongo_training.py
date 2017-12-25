# -*- coding: utf-8 -*-
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
from pattern.en import tokenize as p_tokenize
from nltk import tokenize as n_tokenize
from nltk.corpus import stopwords
from time import time, sleep
from gensim.models.phrases import Phrases, Phraser
from timeit import default_timer
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

common_terms = ["of", "with", "without", "and", "or", "the", "a", "an"]


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


def parse_sent(sentence):
    """parse sentence to list of words
    """
    # remove whitespace at the beginning
    sline = sentence.strip()
    # remove % sign
    # sline = sline.strip("%")
    # sline = sline.rstrip("'s")
    rline = cleanhtml(sline)
    # tokenize lines
    tokenized_line = ' '.join(p_tokenize(rline))
    # parse digits, remove signs
    is_alpha_word_line = [
        word for word in tokenized_line.lower().split() if word.isalpha()
    ]

    return is_alpha_word_line


user = "wiki"
password = "root"
host = "192.168.1.73"
uri = "mongodb://%s:%s@%s" % (quote_plus(user), quote_plus(password), host)
client = MongoClient(uri)
from sshtunnel import SSHTunnelForwarder
import pymongo
import pprint

MONGO_HOST = "192.168.1.73"
MONGO_DB = "wiki"
MONGO_USER = "wiki"
MONGO_PASS = "root"

server = SSHTunnelForwarder(
    MONGO_HOST,
    ssh_username=MONGO_USER,
    ssh_password=MONGO_PASS,
    remote_bind_address=('127.0.0.1', 27017))

server.start()

# client = pymongo.MongoClient('127.0.0.1', server.local_bind_port) # server.local_bind_port is assigned local port
# db = client[MONGO_DB]
# pprint.pprint(db.collection_names())

# server.stop()
pages_file_path = '/home/weiwu/share/deep_learning/data/corporate_finance_level_2.csv'
ls_pageid = pd.read_csv(pages_file_path).pageid.values

# client = MongoClient('mongodb://localhost:27017/')
db = client['wiki']
collection = db.wiki

# pprint.pprint(collection.find_one({"page_id": 12}))
# page_num = 0
# for page_id in ls_pageid:
#     try:
#         pprint.pprint(collection.find_one({"page_id": page_id})['title'])
#     except TypeError:
#         continue
#     else:
#         page_num = page_num + 1

process_count = multiprocessing.cpu_count()


class MySentences(object):
    """lines -> sentence list(['...', '...',...]) ->
    words list([[[' '],[' ']],[[' '],[' ']],...) ->
    phrase([['a_b','c_d']])"""

    def __init__(self, common_terms):
        self.bigram = Phrases(
            min_count=2, threshold=5, common_terms=common_terms)
        self.page_num = 0
        self.load_start = default_timer()

    def __iter__(self):
        for page_id in ls_pageid:
            try:
                # pprint.pprint(collection.find_one({"page_id": page_id})['title'])
                article = collection.find_one({"page_id": page_id})
                page = article['text']
                sentences = n_tokenize.sent_tokenize(page)
                sentence_stream = [parse_sent(doc) for doc in sentences]
                self.bigram.add_vocab(sentence_stream)
                sentence_stream = list(self.bigram[sentence_stream])
                for sent in sentence_stream:
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


pages = MySentences(common_terms)
model = gensim.models.Word2Vec(
    pages,
    size=200,
    window=10,
    min_count=10,
    workers=multiprocessing.cpu_count())

#for k in pages:
#    print(k)

# for root, dirs, files in os.walk(self.dirname):
#     for filename in files:
#         file_path = root + '/' + filename
#         with open(file_path, 'rb') as f:
#             # read all lines in the file as a list
#             readlines = f.readlines()

#         sentence_stream = [parse_sent(doc) for doc in readlines]
#         self.bigram.add_vocab(sentence_stream)
#         # bigram = Phrases(
#         #     sentence_stream,
#         #     min_count=2,
#         #     threshold=5,
#         #     common_terms=common_terms)
#         sentence_stream = list(self.bigram[sentence_stream])
#         for sent in sentence_stream:
#             yield sent

# sentences = MySentences(data_path, common_terms)
