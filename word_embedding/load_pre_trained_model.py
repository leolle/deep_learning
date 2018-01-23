# -*- coding: utf-8 -*-
from __future__ import print_function
from gensim.models import KeyedVectors
from gensim.models import Word2Vec
from gensim.models.word2vec import LineSentence
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
# phrase_filename = '/home/weiwu/share/deep_learning/data/model/phrase/enwiki_economy_pages_only/word2vec_org'

# google_filename = '/home/weiwu/share/deep_learning/data/GoogleNews-vectors-negative300.bin'
# finance_level5_filename = '/home/weiwu/share/deep_learning/data/model/phrase/word2vec_org_finance_level_5'
# # model_wiki = KeyedVectors.load_word2vec_format(wiki_filename, binary=False)
# model_level5 = KeyedVectors.load_word2vec_format(
#     finance_level5_filename, binary=False)
# model_phrase = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
# model_wiki.most_similar(positive=['commodity', 'pound'], negative=['gold'], topn=10)

# model_wiki.most_similar(positive=['gold', 'commodity'], negative=['dollar'], topn=10)
# model_wiki.doesnt_match("cpi gdp interest lunch".split())
#model_google = KeyedVectors.load_word2vec_format(google_filename, binary=True)
# result = model_wiki.most_similar(
#     positive=['woman', 'king'], negative=['man'], topn=1)
# pprint.pprint(result)
# pprint.pprint(model_wiki.most_similar(['gdp'], topn=10))
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


# # test_similarity(model=model_google)
# test_similarity(model=model_phrase)
# test_similarity(model=model_level5)

zh_wiki_file = '/home/weiwu/share/deep_learning/data/model/phrase/zhwiki/word2vec_org_whole_wiki_corpus_user_dict_m5'
zh_wiki_file_level_3 = '/home/weiwu/share/deep_learning/data/model/phrase/zhwiki/word2vec_org_level_3_finance_no_parsing'
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
