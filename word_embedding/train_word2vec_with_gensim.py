#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pan Yang (panyangnlp@gmail.com)
# Copyright 2017 @ Yu Zhen

import gensim
import logging
import multiprocessing
import os
import re
import sys

from pattern.en import tokenize as p_tokenize
from nltk import tokenize as n_tokenize
from time import time, sleep
from gensim.models.phrases import Phrases, Phraser

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
                    ls_sent = n_tokenize.sent_tokenize(rline)

                    logging.info("here is paragraph: %s\n", ls_sent)
                    #sleep(3)
                    # words = []
                    # for sent in ls_sent:
                    sentence_stream = [doc.split(" ") for doc in ls_sent]
                    phrases = Phrases(sentence_stream, min_count=1, threshold=2)
                    bigram = Phraser(phrases)
                    logging.info(list(bigram[sentence_stream]))
                    # tokenized_line = ' '.join(p_tokenize(ls_sent))
                    # logging.info('here is sentences: %s %s',
                    #              type(tokenized_line), len(tokenized_line))
                    # is_alpha_word_line = [
                    #     word for word in tokenized_line.lower().split()
                    #     if word.isalpha()
                    # ]
                    # yield is_alpha_word_line


if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("Please use python train_with_gensim.py data_path")
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
    model.save("/home/weiwu/share/deep_learning/data/model/word2vec_gensim")
    model.wv.save_word2vec_format(
        "/home/weiwu/share/deep_learning/data/model/word2vec_org",
        "/home/weiwu/share/deep_learning/data/model/vocabulary",
        binary=False)

    end = time()
    print("Total procesing time: %d seconds" % (end - begin))
