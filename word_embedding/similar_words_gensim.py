# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors, Word2Vec
from gensim.models.phrases import Phrases, Phraser
import os
import itertools
import re
from nltk import tokenize as n_tokenize
from pattern.en import tokenize as p_tokenize
import pprint
import multiprocessing

text = u'''the mayor of new york was there. machine learning can be useful sometimes. The titular threat of The Blob has always struck me as the ultimate movie monster. an insatiably hungry, amoeba-like mass able to penetrate virtually any safeguard, capable of--as a doomed doctor chillingly describes it--"assimilating flesh on contact. Snide comparisons to gelatin be damned.
'''


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


def parse_sent(sentence):
    """parse sentence to list of words
    """
    # remove whitespace at the beginning
    sline = sentence.strip()
    # remove % sign
    # sline = sline.strip("%")
    # sline = sline.rstrip("'s")
    rline = cleanhtml(sline)
    # tokenize lines
    tokenized_line = ' '.join(p_tokenize(rline))
    # parse digits, remove signs
    is_alpha_word_line = [
        word for word in tokenized_line.lower().split() if word.isalpha()
    ]

    return is_alpha_word_line


# sentence_stream = [[
#     u'the', u'mayor', u'of', u'new', u'york', u'was', u'there'
# ], [u'machine', u'learning', u'can', u'be', u'useful', u'sometimes'],
#                    ['new', 'york', 'mayor', 'was', 'present']]
# phrases = Phrases(sentence_stream, min_count=1, threshold=2)
# bigram = Phraser(phrases)
# sent = [u'the', u'mayor', u'of', u'new', u'york', u'was', u'there']
# pprint.pprint(bigram[sent])
# print('\n')
# pprint.pprint(list(bigram[sentence_stream]))

import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

cur_dir = os.getcwd()
glove_path = '/home/weiwu/share'
name = 'computer_age_statis.pdf'
file_name = os.path.join(cur_dir + '/data/docs/', name)
txt_file = os.path.join(cur_dir, name)

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
# bigram = Phraser(phrases, common_terms=common_terms)
# sent = [u'the', u'mayor', u'of', u'new', u'york', u'was', u'there']
# pprint.pprint(bigram[sent])
print('\n')
# pprint.pprint(list(bigram[words]))

# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=2)
# model.most_similar(['titular'])
# model.save('text8.model')
# model.wv.save_word2vec_format('text.model.bin', binary=True)

# more_examples = ["he is she", "big bigger bad", "going went being"]
# for example in more_examples:
#     a, b, x = example.split()
#     predicted = model.most_similar([x, b], [a])[0][0]
#     print("'%s' is to '%s' as '%s' is to '%s'" % (a, b, x, predicted))

# for _ in words:
#     phrases = Phrases(_, min_count=1, threshold=2)
#     print(phrases[_])

from gensim import utils, interfaces
from gensim.models import Phrases  # noqa:F811 for pickle
from gensim.models.word2vec import Text8Corpus
# sentences = Text8Corpus('text8)

# test_doc = LineSentence('test/test_data/testcorpus.txt')
sentence_stream = [doc.split(" ") for doc in sentences]

# bigram = Phrases(sentences, min_count=1, threshold=2)
bigram = Phrases(sentences, min_count=1, threshold=2, common_terms=common_terms)
# for s in bigram[sentences]:
#     print(utils.to_utf8(u' '.join(s)))
"""-------------------------------------------------------------------------"""
from gensim.models import Phrases
documents = [
    "the mayor of new york was there",
    "the machine of learning method can be useful sometimes",
    "new york mayor was present", "the mayor shows his lack of interest",
    "I love machine learning very much"
]

sentence_stream = [doc.split(" ") for doc in documents]
bigram = Phrases(
    sentence_stream, min_count=1, threshold=2, common_terms=common_terms)
sent = [u'the', u'mayor', u'of', u'new', u'york', u'was', u'there']
print(bigram[sent])
"""------------------------------------------------------------------------"""
file_path = '/home/weiwu/share/deep_learning/data/enwiki/AA/'

# with open(file_path, 'rb') as f:
#     read_data = f.readline()
#     print read_data

# wiki = open(file_path, 'rb')
# documents = wiki.readlines()
# wiki.close()

# with open(file_path, 'rb') as f:
#     whole_string = f.read()
# print whole_string[:1000]
# print sentences_transedback[:1000]


def parse(sentence):
    # remove whitespace at the beginning
    sline = sentence.strip()
    # remove % sign
    sline = sline.strip("%")
    rline = cleanhtml(sline)

    tokenized_line = ' '.join(p_tokenize(rline))
    is_alpha_word_line = [
        word for word in tokenized_line.lower().split() if not word.isdigit()
    ]

    return is_alpha_word_line


sentence_stream = [parse(doc) for doc in documents]
bigram = Phrases(
    sentence_stream, min_count=5, threshold=10, common_terms=common_terms)
from itertools import chain
strings_sent = list(bigram[sentence_stream])

# print " ".join(chain.from_iterable(strings))
sentences_transedback = " ".join(chain.from_iterable(strings_sent))

# model = word2vec.Word2Vec(strings_sent, size=200)


class MySentences(object):
    """lines -> sentence list(['...', '...',...]) ->
    words list([[[' '],[' ']],[[' '],[' ']],...) ->
    phrase([['a_b','c_d']])"""

    def __init__(self, dirname, common_terms):
        self.dirname = dirname
        self.bigram = Phrases(
            min_count=2, threshold=5, common_terms=common_terms)

    def __iter__(self):
        for root, dirs, files in os.walk(self.dirname):
            for filename in files:
                print filename
                file_path = root + '/' + filename
                with open(file_path, 'rb') as f:
                    # read all lines in the file as a list
                    readlines = f.readlines()

                sentence_stream = [parse_sent(doc) for doc in readlines]
                self.bigram.add_vocab(sentence_stream)
                sentence_stream = list(self.bigram[sentence_stream])
                for sent in sentence_stream:
                    yield sent


phrase_filename = '/home/weiwu/share/deep_learning/data/model/phrase/word2vec_org'
# model_phrase = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
# model_google = KeyedVectors.load_word2vec_format(google_filename, binary=True)

sentences = MySentences(file_path, common_terms)
model = Word2Vec(
    sentences,
    size=200,
    window=10,
    min_count=10,
    workers=multiprocessing.cpu_count())
# X = model_phrase[model_phrase.wv.vocab]
# # visualize food data
# from sklearn.manifold import TSNE
# import matplotlib.pyplot as plt

# tsne = TSNE(n_components=2)
# X_tsne = tsne.fit_transform(X)
# plt.rcParams['figure.figsize'] = [10, 10]
# plt.scatter(X_tsne[:, 0], X_tsne[:, 1])
# plt.show()
