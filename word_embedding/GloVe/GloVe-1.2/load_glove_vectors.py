# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
import pandas as pd
import csv
import os
import itertools
from gensim.models.word2vec import Text8Corpus
from glove import Corpus, Glove

import logging
logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def loadGloveModel(gloveFile):
    print("Loading Glove Model")
    f = open(gloveFile, 'r')
    model = {}
    for line in f:
        splitLine = line.split()
        word = splitLine[0]
        embedding = np.array([float(val) for val in splitLine[1:]])
        model[word] = embedding
    print("Done.", len(model), " words loaded!")
    return model


# The GloVe dump from the Stanford site is in a format that is little different from the word2vec format. You can # convert the GloVe file into word2vec format using:
# python -m gensim.scripts.glove2word2vec --input  glove.840B.300d.txt --output glove.840B.300d.w2vformat.txt
path = '/home/weiwu/projects/deep_learning/word_embedding/GloVe/GloVe-1.2'
glove_path = '/home/weiwu/share'
name = 'vectors.bin'
file_name = os.path.join(path, name)
txt_name = 'vectors.txt'
w2v_txt_name = 'vectors.w2vformat.txt'
txt_file = os.path.join(path, txt_name)
w2v_txt_file = os.path.join(path, w2v_txt_name)
# model = loadGloveModel(txt_name)
#words = pd.read_table(
#    w2v_txt_file, sep=" ", index_col=0, header=None, quoting=csv.QUOTE_NONE)
# words_matrix = words.as_matrix()
#model = KeyedVectors.load_word2vec_format(
#    os.path.join(path, 'vectors.w2vformat.txt'), binary=True)
# model.most_similar('the')
'''''' '''''' '''''' '''''' ''
#sentences = word2vec.Text8Corpus('text8')
#model = word2vec.Word2Vec(sentences, size=200)
#model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
#model.most_similar(positive=['woman', 'king'], negative=['man'], topn=2)
#model.most_similar(['man'])
#model.save('text8.model')
#model.wv.save_word2vec_format('text.model.bin', binary=True)
model1 = KeyedVectors.load_word2vec_format('text.model.bin', binary=True)
model1.most_similar(['girl', 'father'], ['boy'], topn=3)
more_examples = ["he is she", "big bigger bad", "going went being"]
for example in more_examples:
    a, b, x = example.split()
    predicted = model1.most_similar([x, b], [a])[0][0]
    print("'%s' is to '%s' as '%s' is to '%s'" % (a, b, x, predicted))

sentences = list(itertools.islice(Text8Corpus('text8'), None))
corpus = Corpus()
corpus.fit(sentences, window=10)
glove = Glove(no_components=100, learning_rate=0.05)
glove.fit(corpus.matrix, epochs=30, no_threads=4, verbose=True)
