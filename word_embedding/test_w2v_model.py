# -*- coding: utf-8 -*-
from __future__ import print_function
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
import os
import logging
user_path = os.path.expanduser("~")

logger = logging.getLogger()
handler = logging.StreamHandler()
formatter = logging.Formatter(
    '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)
    logger.setLevel(logging.DEBUG)
finance_vocab = [
    'sales', 'gdp', 'sales', 'revenue', 'growth_rate', 'net_income',
    'cash_flow', 'debt', 'assets', 'dividend_yield', 'llc', 'firm', 'earnings',
    'book_value', 'interest_rate'
]
zh_finance_vocab = [
    u'销售', u'营业额', u'收入', u'增长率', u'净收入', u'现金流', u'负债', u'资产', u'股息率', u'公司',
    u'有限公司', u'盈利', u'账面', u'价值', u'利率'
]
topn = 20


def test_similarity(vocabs, model, topn=topn):
    for vocab in vocabs:
        try:
            result = model.most_similar(vocab, topn=topn)
        except KeyError:
            print('%s does not exist in vocabulary' % vocab)
            print("\n")
        else:
            print("top %s similar vocabulary of %s" % (topn, vocab))
            for e in result:
                print(e[0], e[1])
            print("\n")


zh_wiki_file = user_path + '/share/deep_learning/data/model/phrase/zhwiki/word2vec_org_whole_wiki_corpus_user_dict_m5'
zh_wiki_file_level_3 = './data/'
# model_zhwiki_level_3 = KeyedVectors.load_word2vec_format(\
#                                                         zh_wiki_file_level_3, binary=False)
model_zhwiki = KeyedVectors.load_word2vec_format(zh_wiki_file, binary=False)
test_similarity(vocabs=zh_finance_vocab, model=model_zhwiki)
#test_similarity(vocabs=zh_finance_vocab, model=model_zhwiki_level_3)

result = model_zhwiki.most_similar(u"责任有限公司", topn=10)
for e in result:
    print(e[0], e[1])

# zh_wiki_corpus = '/home/weiwu/share/deep_learning/data/wiki.zh.text.simple.clean.seg'
# sentences = LineSentence(zh_wiki_corpus)
