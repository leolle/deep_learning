#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pan Yang (panyangnlp@gmail.com)
# Copyright 2017 @ Yu Zhen

import gensim
from gensim.models.phrases import Phrases
import logging
import multiprocessing
import os
import re
import sys

from nltk.corpus import stopwords
from pattern.en import tokenize
from time import time

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def cleanhtml(raw_html):
    cleanr = re.compile('<.*?>')
    cleantext = re.sub(cleanr, ' ', raw_html)
    return cleantext


class MySentences(object):

    def __init__(self, dirname):
        self.dirname = dirname

    def __iter__(self):
        for root, dirs, files in os.walk(self.dirname):
            for filename in files:
                file_path = root + '/' + filename
                for line in open(file_path):
                    sline = line.strip()
                    if sline == "":
                        continue
                    rline = cleanhtml(sline)
                    # tokenize the line, remove
                    tokenized_line = ' '.join(tokenize(rline))
                    is_alpha_word_line = [
                        word for word in tokenized_line.lower().split()
                        if word.isalpha() and
                        word not in stopwords.words('english')
                    ]
                    yield is_alpha_word_line


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please use python train_word2vec_txt.py data_path")
        exit()
    data_path = sys.argv[1]
    begin = time()

    sentences = MySentences(data_path)
    model = gensim.models.Word2Vec(
        sentences,
        size=200,
        window=10,
        min_count=10,
        workers=multiprocessing.cpu_count())
    #     model.save("/home/weiwu/share/deep_learning/data/model/word2vec_txt_gensim")
    model.wv.save_word2vec_format(
        "/home/weiwu/share/deep_learning/data/model/word2vec_txt_org",
        "/home/weiwu/share/deep_learning/data/model/vocabulary_txt",
        binary=False)

    end = time()
    print("Total procesing time: %d seconds" % (end - begin))
