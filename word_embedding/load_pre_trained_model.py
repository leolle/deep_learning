# -*- coding: utf-8 -*-
from __future__ import print_function
from gensim.models import KeyedVectors
import pprint
import logging

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
    phrase_filename = '/home/weiwu/share/deep_learning/data/model/phrase/enwiki_economy/word2vec_org'

google_filename = '/home/weiwu/share/deep_learning/data/GoogleNews-vectors-negative300.bin'
finance_level5_filename = '/home/weiwu/share/deep_learning/data/model/phrase/word2vec_org_finance_level_5'
# model_wiki = KeyedVectors.load_word2vec_format(wiki_filename, binary=False)
model_level5 = KeyedVectors.load_word2vec_format(
    finance_level5_filename, binary=False)
model_phrase = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
model_google = KeyedVectors.load_word2vec_format(google_filename, binary=True)
# result = model_wiki.most_similar(
#     positive=['woman', 'king'], negative=['man'], topn=1)
# pprint.pprint(result)
# pprint.pprint(model_wiki.most_similar(['gdp'], topn=10))
finance_vocab = [
    'sales', 'gdp', 'sales', 'revenue', 'growth_rate', 'net_income',
    'cash_flow', 'debt', 'assets', 'dividend_yield', 'llc', 'firm', 'earnings',
    'book_value', 'interest_rate'
]
topn = 20


def test_similarity(model=model_phrase, topn=topn):
    for vocab in finance_vocab:
        try:
            print("%s's top %s similar vocabulary" % (vocab, topn))
            pprint.pprint(model.most_similar([vocab], topn=20))
            print("\n")
        except KeyError:
            print('does not exist in vocabulary')


test_similarity(model=model_google)
test_similarity(model=model_phrase)
test_similarity(model=model_level5)


# -*- coding: utf-8 -*-
import sys
import numpy as np
import tensorflow as tf
from datetime import datetime
device_name = sys.argv[1]  # Choose device from cmd line. Options: gpu or cpu
shape = (int(sys.argv[2]), int(sys.argv[2]))
if device_name == "gpu":
    device_name = "/gpu:0"
else:
    device_name = "/cpu:0"
 
with tf.device(device_name):
    random_matrix = tf.random_uniform(shape=shape, minval=0, maxval=1)
    dot_operation = tf.matmul(random_matrix, tf.transpose(random_matrix))
    sum_operation = tf.reduce_sum(dot_operation)
 
 
startTime = datetime.now()
with tf.Session(config=tf.ConfigProto(log_device_placement=True)) as session:
        result = session.run(sum_operation)
        print(result)
 
# It can be hard to see the results on the terminal with lots of output -- add some newlines to improve readability.
print("\n" * 5)
print("Shape:", shape, "Device:", device_name)
print("Time taken:", datetime.now() - startTime)
 
print("\n" * 5)
