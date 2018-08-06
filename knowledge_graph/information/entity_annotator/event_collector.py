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
zh_finance_vocab = ['投资', '设立', '增资', '入股', '收购', '并购', '换股']
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


analyst_report_model_path = user_path + '/share/deep_learning/data/model/analyst_report.w2v_org'
analyst_report_model = KeyedVectors.load_word2vec_format(
    analyst_report_model_path, binary=False)
# model_zhwiki = KeyedVectors.load_word2vec_format(zh_wiki_file, binary=False)
test_similarity(vocabs=zh_finance_vocab, model=analyst_report_model)
#test_similarity(vocabs=zh_finance_vocab, model=model_zhwiki_level_3)

# result = analyst_report_model.most_similar(u"互联网", topn=10)
# for e in result:
#     print(e[0], e[1])
