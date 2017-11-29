# -*- coding: utf-8 -*-
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
    '/home/weiwu/share/deep_learning/data/Combined_News_DJIA.csv')
na_str_DJA_news = DJA_news.iloc[:, 2:].values
na_str_DJA_news = na_str_DJA_news.flatten()
na_str_reddit_news = reddit_news.News.values
sentences_reddit = [s.encode('utf-8').split() for s in na_str_reddit_news]
sentences_DJA = [s.encode('utf-8').split() for s in na_str_DJA_news]
# for s in na_str_DJA_news:
#     if s is float:
#         continue
#     [s.encode('utf-8').split()]
model = word2vec.Word2Vec(sentences_DJA, size=200)
