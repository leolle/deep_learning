# -*- coding: utf-8 -*-
from __future__ import print_function
from gensim.models import KeyedVectors
import pprint
google_filename = '/home/weiwu/share/deep_learning/data/GoogleNews-vectors-negative300.bin'
phrase_filename = '/home/weiwu/share/deep_learning/data/model/phrase/word2vec_org'
wiki_filename = '/home/weiwu/share/deep_learning/data/model/word2vec_org'
model_wiki = KeyedVectors.load_word2vec_format(wiki_filename, binary=False)
model_phrase = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
#model_google = KeyedVectors.load_word2vec_format(google_filename, binary=True)
# result = model_wiki.most_similar(
#     positive=['woman', 'king'], negative=['man'], topn=1)
# pprint.pprint(result)
pprint.pprint(model_wiki.most_similar(['gdp'], topn=10))
pprint.pprint(model_phrase.most_similar(['gdp'], topn=10))
