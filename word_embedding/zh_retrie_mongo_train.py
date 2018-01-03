# encoding: utf-8
import codecs
import jieba

str_in = "小明硕士毕业于中国科学院计算所，\
后在日本京都大学深造，凭借过人天赋，旁人若在另一方面爱他，他每即躲开。"

stopwords = codecs.open('stopwords', 'r', 'utf-8').read().split(',')
seg_list = jieba.cut(str_in, cut_all=False)
for seg in seg_list:
    if seg not in stopwords:
        print(seg)
