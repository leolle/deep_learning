# -*- coding: utf-8 -*-
from __future__ import print_function
from gensim.models import KeyedVectors
import pprint
filename = '/home/weiwu/share/deep_learning/data/GoogleNews-vectors-negative300.bin'
model = KeyedVectors.load_word2vec_format(filename, binary=True)
result = model.most_similar(
    positive=['woman', 'king'], negative=['man'], topn=1)
pprint.pprint(result)
pprint.pprint(model.most_similar(['gdp'], topn=50))
