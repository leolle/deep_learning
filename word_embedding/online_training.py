# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
from gensim.models.phrases import Phrases, Phraser
from gensim import utils, interfaces
from gensim.models import Phrases  # noqa:F811 for pickle
from gensim.models.word2vec import Text8Corpus
import os
import itertools
import re
from nltk import tokenize as n_tokenize
from pattern.en import tokenize as p_tokenize
import pprint
import multiprocessing

import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

text = u'''the mayor of new york was there. machine learning can be useful sometimes. The titular threat of The Blob has always struck me as the ultimate movie monster. an insatiably hungry, amoeba-like mass able to penetrate virtually any safeguard, capable of--as a doomed doctor chillingly describes it--"assimilating flesh on contact. Snide comparisons to gelatin be damned.
'''


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


sentences = word2vec.Text8Corpus('text8')
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
# print '\n-----\n'.join(tokenizer.tokenize(text))
words = []
sentences = n_tokenize.sent_tokenize(text)
for line in sentences:
    sline = line.strip()
    if sline == "":
        continue
    rline = cleanhtml(sline)
    tokenized_line = ' '.join(p_tokenize(rline))
    is_alpha_word_line = [
        word for word in tokenized_line.lower().split() if word.isalpha()
    ]
    words.append(is_alpha_word_line)
common_terms = ["of", "with", "without", "and", "or", "the", "a", "an"]
phrases = Phrases(words, min_count=1, threshold=2, common_terms=common_terms)
