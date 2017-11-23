# -*- coding: utf-8 -*-
import numpy as np
from gensim.models import word2vec
from gensim.models import KeyedVectors
import pandas as pd
import csv
import os


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
name = 'vectors.bin'
file_name = os.path.join(path, name)
# model = word2vec.Word2Vec.load_word2vec_format(
#     file_name, binary=True, unicode_errors='ignore')
# model = KeyedVectors.load_word2vec_format(file_name, binary=True)
txt_name = '/home/weiwu/share/glove.6B.100d.txt'
model = loadGloveModel(txt_name)

words = pd.read_table(
    txt_name, sep=" ", index_col=0, header=None, quoting=csv.QUOTE_NONE)
words_matrix = words.as_matrix()
