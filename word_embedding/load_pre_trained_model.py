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

zh_wiki_file = '/home/weiwu/share/deep_learning/data/model/phrase/zhwiki/word2vec_org_whole_wiki_corpus'
model_wiki = KeyedVectors.load_word2vec_format(zh_wiki_file, binary=False)
