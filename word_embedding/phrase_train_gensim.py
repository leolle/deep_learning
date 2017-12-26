#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Author: Pan Yang (panyangnlp@gmail.com)
# Copyright 2017 @ Yu Zhen

import gensim
import logging
import multiprocessing
import os
import re
import sys, os

from pattern.en import tokenize as p_tokenize
from nltk import tokenize as n_tokenize
from nltk.corpus import stopwords
from time import time, sleep
from gensim.models.phrases import Phrases, Phraser
import pandas as pd

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)

common_terms = ["of", "with", "without", "and", "or", "the", "a", "an"]


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


def complete_dir_path(dir_path):
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


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
                file_path = root + '/' + filename
                with open(file_path, 'rb') as f:
                    # read all lines in the file as a list
                    readlines = f.readlines()

                sentence_stream = [parse_sent(doc) for doc in readlines]
                self.bigram.add_vocab(sentence_stream)
                # bigram = Phrases(
                #     sentence_stream,
                #     min_count=2,
                #     threshold=5,
                #     common_terms=common_terms)
                sentence_stream = list(self.bigram[sentence_stream])
                for sent in sentence_stream:
                    yield sent


pages_csv = pd.DataFrame()
for root, dirs, files in os.walk(
        '/home/weiwu/share/deep_learning/data/enwiki_categories/'):
    for filename in files:
        file_path = root + '/' + filename
        page_read = pd.read_csv(file_path)
        pages_csv = pd.concat([pages_csv, page_read])

if __name__ == '__main__':
    #
    if len(sys.argv) != 3:
        print("Please use python train_with_gensim.py data_path output_path")
        exit()
    data_path = sys.argv[1]
    output_path = sys.argv[2]
    begin = time()

    sentences = MySentences(data_path, common_terms)
    model = gensim.models.Word2Vec(
        sentences,
        size=200,
        window=10,
        min_count=10,
        workers=multiprocessing.cpu_count())
    model.save(complete_dir_path(output_path) + "word2vec_gensim")
    model.wv.save_word2vec_format(
        complete_dir_path(output_path) + "word2vec_org",
        complete_dir_path(output_path) + "vocabulary",
        binary=False)

    end = time()
    print("Total procesing time: %d seconds" % (end - begin))
