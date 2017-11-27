# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
import os
import itertools
import textract

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


path = '/home/weiwu/projects/deep_learning/word_embedding/GloVe/GloVe-1.2'
glove_path = '/home/weiwu/share'
name = 'vectors.bin'
file_name = os.path.join(path, name)
txt_name = 'vectors.txt'
w2v_txt_name = 'vectors.w2vformat.txt'
txt_file = os.path.join(path, txt_name)
w2v_txt_file = os.path.join(path, w2v_txt_name)


def pdf2text(file_path):
    text = textract.process(file_path)
    return text


sentences = word2vec.Text8Corpus('text8')
model = word2vec.Word2Vec(sentences, size=200)
model.most_similar(positive=['woman', 'king'], negative=['man'], topn=1)
# model.most_similar(positive=['woman', 'king'], negative=['man'], topn=2)
# model.most_similar(['man'])
# model.save('text8.model')
# model.wv.save_word2vec_format('text.model.bin', binary=True)

more_examples = ["he is she", "big bigger bad", "going went being"]
for example in more_examples:
    a, b, x = example.split()
    predicted = model.most_similar([x, b], [a])[0][0]
    print("'%s' is to '%s' as '%s' is to '%s'" % (a, b, x, predicted))
