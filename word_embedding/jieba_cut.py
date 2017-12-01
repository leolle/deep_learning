#!/usr/bin/env python
#-*- coding:utf-8 -*-
import jieba
import jieba.analyse
import jieba.posseg as pseg


def cut_words(sentence):
    #print sentence
    return " ".join(jieba.cut(sentence)).encode('utf-8')


f = open("wiki.zh.text.jian")
target = open("wiki.zh.text.jian.seg", 'a+')
print 'open files'
line = f.readlines(100000)
while line:
    curr = []
    for oneline in line:
        #print(oneline)
        curr.append(oneline)
    '''
    seg_list = jieba.cut_for_search(s)
    words = pseg.cut(s)
    for word, flag in words:
        if flag != 'x':
            print(word)
    for x, w in jieba.analyse.extract_tags(s, withWeight=True):
        print('%s %s' % (x, w))
    '''
    after_cut = map(cut_words, curr)
    # print lin,
    #for words in after_cut:
    #print words
    target.writelines(after_cut)
    print 'saved 100000 articles'
    line = f.readlines(100000)
f.close()
target.close()
