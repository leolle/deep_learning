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

# google_filename = '/home/weiwu/share/deep_learning/data/GoogleNews-vectors-negative300.bin'
# wiki_filename = '/home/weiwu/share/deep_learning/data/model/word2vec_org'
# model_wiki = KeyedVectors.load_word2vec_format(wiki_filename, binary=False)
model_phrase = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
#model_google = KeyedVectors.load_word2vec_format(google_filename, binary=True)
# result = model_wiki.most_similar(
#     positive=['woman', 'king'], negative=['man'], topn=1)
# pprint.pprint(result)
# pprint.pprint(model_wiki.most_similar(['gdp'], topn=10))
finance_vocab = [
    'sales', 'gdp', 'sales', 'revenue', 'growth_rate', 'net_income',
    'discount_rate', 'cash_flow', 'debt', 'assets', 'dividend_yield',
    'peg_ratio', 'llc', 'firm', 'corporate', 'earnings', 'book_value',
    'interest_rate'
]
for vocab in finance_vocab:
    print(vocab)
    pprint.pprint(model_phrase.most_similar([vocab], topn=20))
