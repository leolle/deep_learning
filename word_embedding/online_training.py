# -*- coding: utf-8 -*-
import numpy as np
from gensim.matutils import unitvec
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
import numpy as np
import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

text = u'''the mayor of new york was there. machine learning can be useful sometimes. The titular threat of The Blob has always struck me as the ultimate movie monster. an insatiably hungry, amoeba-like mass able to penetrate virtually any safeguard, capable of--as a doomed doctor chillingly describes it--"assimilating flesh on contact. Snide comparisons to gelatin be damned.
'''
text_add = u'''To bring out hidden structure in the corpus, discover relationships between words and use them to describe the documents in a new and (hopefully) more semantic way.
To make the document representation more compact. This both improves efficiency (new representation consumes less resources) and efficacy (marginal data trends are ignored, noise-reduction).
'''


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


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


# sentences = word2vec.Text8Corpus('text8')
import nltk.data
tokenizer = nltk.data.load('tokenizers/punkt/english.pickle')
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
phrases = Phrases(words, min_count=1, threshold=1)
sentence_stream = [doc.split(" ") for doc in sentences]
strings_sent = list(phrases[sentence_stream])
phrase_filename = '/home/weiwu/share/deep_learning/data/model/phrase/word2vec_org'
# model_phrase = KeyedVectors.load_word2vec_format(phrase_filename, binary=False)
# generate the Word2Vec model
model = word2vec.Word2Vec(strings_sent, min_count=1, size=300)
google_filename = '/home/weiwu/share/deep_learning/data/GoogleNews-vectors-negative300.bin'
model_google = KeyedVectors.load_word2vec_format(google_filename, binary=True)

more_sentences = n_tokenize.sent_tokenize(text_add)
more_sentences = [doc.lower().split(" ") for doc in more_sentences]

model.init_sims(replace=True)
model.build_vocab(more_sentences, update=True)
model.train(
    more_sentences, total_examples=model.corpus_count, epochs=model.iter)
print("new vocabulary: \n", model.wv.vocab)
"""--------------------------------------------------------------"""


def word_averaging(wv, words):
    all_words, mean = set(), []

    for word in words:
        if isinstance(word, np.ndarray):
            mean.append(word)
        elif word in wv.vocab:
            mean.append(wv.syn0norm[wv.vocab[word].index])
            all_words.add(wv.vocab[word].index)
            print "biswa"

    if not mean:
        logging.warning("cannot compute similarity with no input %s", words)
        # FIXME: remove these examples in pre-processing
        return np.zeros(wv.layer_size,)

    mean = unitvec(np.array(mean).mean(axis=0)).astype(np.float32)
    print mean
    return mean


def word_averaging_list(wv, text_list):
    return np.vstack([word_averaging(wv, review) for review in text_list])


X_train_word_average = word_averaging_list(model_google, more_sentences)
"""--------------------------------------------------------"""


class MySentences(object):
    """lines -> sentence list(['...', '...',...]) ->
    words list([[[' '],[' ']],[[' '],[' ']],...) ->
    phrase([['a_b','c_d']])"""

    def __init__(self, dirname):
        self.dirname = dirname
        self.bigram = Phrases(min_count=2, threshold=5)

    def __iter__(self):
        for root, dirs, files in os.walk(self.dirname):
            for filename in files:
                file_path = root + '/' + filename
                with open(file_path, 'rb') as f:
                    # read all lines in the file as a list
                    readlines = f.readlines()

                sentence_stream = [parse_sent(doc) for doc in readlines]
                self.bigram.add_vocab(sentence_stream)
                sentence_stream = list(self.bigram[sentence_stream])
                for sent in sentence_stream:
                    yield sent


"""----------------------------------------------------------"""
# only intersect words with google, not update
model.intersect_word2vec_format(google_filename, lockf=1.0, binary=True)
model.train(sentences, total_examples=model.corpus_count, epochs=model.iter)
