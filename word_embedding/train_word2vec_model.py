#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Thu Apr 12 17:19:18 CST 2018
fetch all the page from field csv files, pack them to a file.
preprocess text file to tokenized string,
then feed it to gensim word embedding train function.
"""
from tempfile import gettempdir
import gensim
import logging
import multiprocessing
import os
import sys
from time import time, sleep
from timeit import default_timer
from gensim.models.word2vec import LineSentence
from tqdm import tqdm
from gensim.models import KeyedVectors
from ylib.preprocessing import preprocess_string, cut_article, remove_stopwords, strip_punctuation, tokenize, strip_numeric, filter_speech_tag
user_path = os.path.expanduser("~")

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)
filters = [
    cut_article, strip_punctuation, strip_numeric, remove_stopwords, tokenize,
    filter_speech_tag
]

# allow_speech_tags = ['an', 'n', 'nt', 'x', 'eng', 'nt', 'nz']


def complete_dir_path(dir_path):
    if not dir_path.endswith('/'):
        return dir_path + '/'
    else:
        return dir_path


input_path = '/home/weiwu/projects/deep_learning/knowledge_graph/database/data/research_converted.txt'
with open(input_path, 'r') as fp:
    text = fp.read()
    text = preprocess_string(text, filters=filters)
tmp_dir = gettempdir()
output = open(tmp_dir + '/test.txt', 'wb')
output.write(text.encode('utf-8'))
output.close()
txt_path = tmp_dir + '/test.txt'

model = gensim.models.Word2Vec(
    LineSentence(txt_path),
    size=200,
    window=5,
    min_count=1,
    workers=multiprocessing.cpu_count())
# class MySentences(object):

#     def __init__(self, dirname):
#         self.dirname = dirname

#     def __iter__(self):
#         for root, dirs, files in os.walk(self.dirname):
#             for filename in files:
#                 file_path = root + '/' + filename
#                 for line in open(file_path):
#                     sline = line.strip()
#                     if sline == "":
#                         continue
#                     rline = cleanhtml(sline)
#                     # tokenize the line, remove
#                     tokenized_line = ' '.join(tokenize(rline))
#                     is_alpha_word_line = [
#                         word for word in tokenized_line.lower().split()
#                         if word.isalpha() and
#                         word not in stopwords.words('english')
#                     ]
#                     yield is_alpha_word_line

if __name__ == '__main__':

    # if len(sys.argv) != 2:
    #     print("Please use python wiki_preprocess.py output_path")
    #     exit()
    #    output_path = sys.argv[1]
    logging.info("start")
    begin = time()

    dir_path = sys.argv[1]
    output_path = sys.argv[2]

    model = gensim.models.Word2Vec(
        LineSentence(input_path),
        size=200,
        window=5,
        min_count=2,
        workers=multiprocessing.cpu_count())
    model.wv.save_word2vec_format(
        complete_dir_path(output_path) + 'research_converted' + ".w2v_org",
        complete_dir_path(output_path) + 'research_converted' + ".vocab",
        binary=False)
    end = time()
    load_duration = end - begin
    logging.info("Total procesing time: %d seconds" % (end - begin))
