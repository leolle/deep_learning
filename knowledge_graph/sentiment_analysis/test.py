# -*- coding: utf-8 -*-
from snownlp import SnowNLP

s = SnowNLP(u'这个东西真心很赞')

# [u'这个', u'东西', u'真心', u'很', u'赞']
print u"分词"
for word in s.words:
    print word

# [(u'这个', u'r'), (u'东西', u'n'),
#  (u'真心', u'd'), (u'很', u'd'),
#  (u'赞', u'Vg')]
print "\nPOS"
for word in s.tags:
    print word[0], word[1]
print "\nsentiment analysis"
print s.sentiments  # 0.9769663402895832 positive的概率

print "\nPinyin"
print s.pinyin  # [u'zhe', u'ge', u'dong', u'xi',
#  u'zhen', u'xin', u'hen', u'zan']

s = SnowNLP(u'「繁體字」「繁體中文」的叫法在臺灣亦很常見。')

s.han  # u'「繁体字」「繁体中文」的叫法
# 在台湾亦很常见。'

text = u'''
中国商务部：2017年四季度购物中心发展指数为67.2，环比上升0.3。2017年，消费对经济的拉动作用进一步显现，实体商业复苏的态势进一步夯实，购物中心发展指数也始终保持在较高水平。未来，经营者应在控制成本支出上进一步调整策略，推动购物中心持续高效发展。
'''

s = SnowNLP(text)
print text
print "\nsentiment analysis"
print s.sentiments  # 0.9769663402895832 positive的概率

text2 = u"""新浪财经讯 1月25日消息，早盘沪指小幅低开后震荡下行，在3520上方得到支撑止跌反弹，创业板指延续强势，早盘低开高走，在1850附近遇阻小幅回落，上证50跌逾1%，沪深300指数(4369.295, -20.59, -0.47%)(4369.2956, -20.59, -0.47%)跌近1%。截止午盘，沪指报3554.40，跌0.14%；深成指报11595.22，跌0.11%；创指报1829.34，涨0.89%. 美元狂跌至89.20一线。"""
s = SnowNLP(text2)
print text2
print "\nsentiment analysis"
print s.sentiments  # 0.9769663402895832 positive的概率

print "\nKeyword Extraction"
for word in s.keywords(3):  # [u'语言', u'自然', u'计算机']
    print word

print "\nSummary"
print s.summary(3)  # [u'因而它是计算机科学的一部分',
#  u'自然语言处理是一门融语言学、计算机科学、
#	 数学于一体的科学',
#  u'自然语言处理是计算机科学领域与人工智能
#	 领域中的一个重要方向']
# print "\nSentence"
# print s.sentences

s = SnowNLP([[u'这篇', u'文章'], [u'那篇', u'论文'], [u'这个']])
s.tf
s.idf
s.sim([u'文章'])  # [0.3756070762985226, 0, 0]
