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
    u'销售',
    u'公司',
    u'有限公司',
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
gs_graph_wiki_model = './data/model/wiki.w2v_org'
model_gs_graph = KeyedVectors.load_word2vec_format(
    gs_graph_wiki_model, binary=False)
# model_zhwiki = KeyedVectors.load_word2vec_format(zh_wiki_file, binary=False)
test_similarity(vocabs=zh_finance_vocab, model=model_gs_graph)
#test_similarity(vocabs=zh_finance_vocab, model=model_zhwiki_level_3)

result = model_gs_graph.most_similar(u"互联网", topn=10)
for e in result:
    print(e[0], e[1])
