# -*- coding: utf-8 -*-
from snownlp import SnowNLP

# s = SnowNLP(u'这个东西真心很赞')

# print('tokenization', s.words)  # [u'这个', u'东西', u'真心',
# #  u'很', u'赞']

# print('targs', s.tags)  # [(u'这个', u'r'), (u'东西', u'n'),
# #  (u'真心', u'd'), (u'很', u'd'),
# #  (u'赞', u'Vg')]

# print('sentiment', s.sentiments)  # 0.9769663402895832 positive的概率

# print("pinyin", s.pinyin)  # [u'zhe', u'ge', u'dong', u'xi',
# #  u'zhen', u'xin', u'hen', u'zan']

# s = SnowNLP(u'「繁體字」「繁體中文」的叫法在臺灣亦很常見。')

# s.han  # u'「繁体字」「繁体中文」的叫法
# # 在台湾亦很常见。'

text = u'''云南铜业股份有限公司（深交所：000878），简称云铜股份、云铜，前身为云南冶炼厂，成立于1958年，1998年改制为股份公司，更名为现称，1998年6月2日于深圳证券交易所上市。公司是中国第四大铜业企业，生产高纯阴极铜、电工用铜线坏、工业硫酸、金锭、银锭、电工用圆铜线、硫酸铜等主产品，并能综合回收金、银、铝、铋、铂、钯等多种有色金属。2007年10月，中国铝业收购云铜母公司云南铜业集团的49%股权，改名“中铝云南铜业集团”。'''
with open('blacklitterman.txt') as f:
    article = f.read()

s = SnowNLP(article)

print('keywords', s.keywords(10))  # [u'语言', u'自然', u'计算机']

print('summary', s.summary(10))  # [u'因而它是计算机科学的一部分',
#  u'自然语言处理是一门融语言学、计算机科学、
#	 数学于一体的科学',
#  u'自然语言处理是计算机科学领域与人工智能
#	 领域中的一个重要方向']
# print('sentences', s.sentences)

# s = SnowNLP([[u'这篇', u'文章'], [u'那篇', u'论文'], [u'这个']])
# print(s.tf)
# print(s.idf)
# print(s.sim([u'文章']))  # [0.3756070762985226, 0, 0]
