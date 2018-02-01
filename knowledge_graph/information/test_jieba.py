# -*- coding: utf-8 -*-
# 分词
# from preprocessing import preprocess_string
# from preprocessing import strip_numeric
# from preprocessing import remove_stopwords
# from preprocessing import strip_punctuation
# from preprocessing import tokenize
from timeit import default_timer
import os
from jieba.analyse import extract_tags, textrank

begin = default_timer()
str_test = u'''云南铜业股份有限公司（深交所：000878），简称云铜股份、云铜，前身为云南冶炼厂，成立于1958年，1998年改制为股份公司，更名为现称，1998年6月2日于深圳证券交易所上市。公司是中国第四大铜业企业，生产高纯阴极铜、电工用铜线坏、工业硫酸、金锭、银锭、电工用圆铜线、硫酸铜等主产品，并能综合回收金、银、铝、铋、铂、钯等多种有色金属。2007年10月，中国铝业收购云铜母公司云南铜业集团的49%股权，改名“中铝云南铜业集团”。'''
with open('blacklitterman.txt') as f:
    article = f.read()
# filter_setting = [tokenize, strip_punctuation]
# text = preprocess_string(str_test, filter_setting)

print("TF-IDF")
for keyword, weight in extract_tags(str_test, topK=10, withWeight=True):
    print('%s %s' % (keyword, weight))

print('\n')
print("Text Rank")
for keyword, weight in textrank(str_test, withWeight=True):
    print('%s %s' % (keyword, weight))

print("TF-IDF")
for keyword, weight in extract_tags(article, topK=10, withWeight=True):
    print('%s %s' % (keyword, weight))

print('\n')
print("Text Rank")
for keyword, weight in textrank(article, withWeight=True):
    print('%s %s' % (keyword, weight))
