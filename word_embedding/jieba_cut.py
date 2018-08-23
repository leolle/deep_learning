#!/usr/bin/env python
#-*- coding:utf-8 -*-
import jieba
import jieba.analyse
import jieba.posseg as pseg
# 引入 word2vec
from gensim.models import word2vec

# 引入日志配置
import logging

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def cut_words(sentence):
    #print sentence
    return " ".join(jieba.cut(sentence)).encode('utf-8')


# 引入数据集
raw_sentences = [u"但由于中文没有像英文那么自带天然的分词", "所以我们第一步采用分词"]
# 切分词汇
sentences = []
for s in raw_sentences:
    tmp = []
    for item in jieba.cut(s):
        tmp.append(item)
    sentences.append(tmp)
# print(sentences)
# 构建模型
# # model = word2vec.Word2Vec(sentences, min_count=1)

# f = open("wiki.zh.text.jian")
# target = open("wiki.zh.text.jian.seg", 'a+')
# print 'open files'
# line = f.readlines(100000)
# while line:
#     curr = []
#     for oneline in line:
#         #print(oneline)
#         curr.append(oneline)
#     '''
#     seg_list = jieba.cut_for_search(s)
#     words = pseg.cut(s)
#     for word, flag in words:
#         if flag != 'x':
#             print(word)
#     for x, w in jieba.analyse.extract_tags(s, withWeight=True):
#         print('%s %s' % (x, w))
#     '''
#     after_cut = map(cut_words, curr)
#     # print lin,
#     #for words in after_cut:
#     #print words
#     target.writelines(after_cut)
#     print 'saved 100000 articles'
#     line = f.readlines(100000)
# f.close()
# target.close()
