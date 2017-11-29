# -*- coding: utf-8 -*-
from pprint import pprint  # pretty-printer
from collections import defaultdict
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
import pandas as pd
import csv
import os
import itertools
from gensim.models.word2vec import Text8Corpus
from glove import Corpus, Glove
from nltk.corpus import brown
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

sentences = brown.words()
# model = word2vec.Word2Vec(sentences, size=200)

# print(model.most_similar(['brown']))
reddit_news = pd.read_csv('/home/weiwu/share/deep_learning/data/RedditNews.csv')
DJA_news = pd.read_csv(
    '/home/weiwu/share/deep_learning/data/Combined_News_DJIA_parsed.csv')
na_str_DJA_news = DJA_news.iloc[:, 2:].values
na_str_DJA_news = na_str_DJA_news.flatten()
ls_str_DJA_news = na_str_DJA_news.tolist()
# na_str_DJA_news = na_str_DJA_news.reshape(-1,1)
na_str_reddit_news = reddit_news.News.values

# sentences_reddit = [s.encode('utf-8').split() for s in na_str_reddit_news]
# sentences_DJA = [s.encode('utf-8').split() for s in na_str_DJA_news]

# remove common words and tokenize
stoplist = set('for a of the and to in'.split())
texts = [[
    word for word in str(document).decode('utf-8').lower().split()
    if word not in stoplist
] for document in ls_str_DJA_news]

# remove words that appear only once
frequency = defaultdict(int)
for text in texts:
    for token in text:
        frequency[token] += 1
texts = [[token for token in text if frequency[token] > 1] for text in texts]
# pprint(texts)
model = word2vec.Word2Vec(texts, size=200)
