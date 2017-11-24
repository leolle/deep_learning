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
glove_path = '/home/weiwu/share'
name = 'vectors.bin'
file_name = os.path.join(path, name)
txt_name = 'vectors.txt'
w2v_txt_name = 'vectors.w2vformat.txt'
txt_file = os.path.join(path, txt_name)
w2v_txt_file = os.path.join(path, w2v_txt_name)
# model = loadGloveModel(txt_name)
words = pd.read_table(
    w2v_txt_file, sep=" ", index_col=0, header=None, quoting=csv.QUOTE_NONE)
# words_matrix = words.as_matrix()
model = KeyedVectors.load_word2vec_format(
    os.path.join(path, 'vectors.w2vformat.txt'), binary=True)
