# -*- coding: utf-8 -*-
# 分词
from pyltp import SentenceSplitter
from preprocessing import preprocess_string
from preprocessing import strip_numeric
from preprocessing import remove_stopwords
from preprocessing import strip_punctuation
from preprocessing import tokenize
from collections import defaultdict
from timeit import default_timer
import os

begin = default_timer()
str_test = u'''云南铜业股份有限公司（深交所：000878），简称云铜股份、云铜，前身为云南冶炼厂，成立于1958年，1998年改制为股份公司，更名为现称，1998年6月2日于深圳证券交易所上市。公司是中国第四大铜业企业，生产高纯阴极铜、电工用铜线坏、工业硫酸、金锭、银锭、电工用圆铜线、硫酸铜等主产品，并能综合回收金、银、铝、铋、铂、钯等多种有色金属。2007年10月，中国铝业收购云铜母公司云南铜业集团的49%股权，改名“中铝云南铜业集团”。'''
str_test = '''中国平安发起成立中小银行互联网金融深圳联盟-新闻-上海证券报·中国'''
filter_setting = [tokenize, strip_punctuation]
text = preprocess_string(str_test, filter_setting)

sents = SentenceSplitter.split(str_test)  # 分句
print('\n'.join(sents))
LTP_DATA_DIR = '/home/weiwu/share/software/ltp_data_v3.4.0'  # ltp模型目录的路径
cws_model_path = os.path.join(LTP_DATA_DIR,
                              'cws.model')  # 分词模型路径，模型名称为`cws.model`

from pyltp import Segmentor
segmentor = Segmentor()  # 初始化实例
segmentor.load(cws_model_path)  # 加载模型
words = segmentor.segment(str_test)  # 分词
print('\t'.join(words))
segmentor.release()  # 释放模型

# 词性标注
from pyltp import Postagger
pos_model_path = os.path.join(LTP_DATA_DIR,
                              'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型

words = text.split()  # 分词结果
postags = postagger.postag(words)  # 词性标注

# print('\t'.join(postags))
postagger.release()  # 释放模型

# 命名实体识别
ner_model_path = os.path.join(LTP_DATA_DIR,
                              'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`

from pyltp import NamedEntityRecognizer
recognizer = NamedEntityRecognizer()  # 初始化实例
recognizer.load(ner_model_path)  # 加载模型

netags = recognizer.recognize(words, postags)  # 命名实体识别

#print('\t'.join(netags))
# # 人名（Nh）、地名（Ns）、机构名（Ni。）
# # B、I、E、S
# ls_organization = [dict_netags[x] for x in ['S-Ni', 'B-Ni', 'E-Ni', 'I-Ni']]
# ls_people = [dict_netags[x] for x in ['S-Nh', 'B-Nh', 'E-Nh', 'I-Nh']]
# ls_geography = [dict_netags[x] for x in ['S-Ns', 'B-Ns', 'E-Ns', 'I-Ns']]
dict_netags = defaultdict(list)
ls_netags = list(zip(netags, words))
for x, y in ls_netags:
    dict_netags[x].append(y)
print(list(zip(words, netags)))
recognizer.release()  # 释放模型

# # 依存句法分析
# par_model_path = os.path.join(LTP_DATA_DIR,
#                               'parser.model')  # 依存句法分析模型路径，模型名称为`parser.model`

# from pyltp import Parser
# parser = Parser()  # 初始化实例
# parser.load(par_model_path)  # 加载模型

# words = ['元芳', '你', '怎么', '看']
# postags = ['nh', 'r', 'r', 'v']
# arcs = parser.parse(words, postags)  # 句法分析

# print("\t".join("%d:%s" % (arc.head, arc.relation) for arc in arcs))
# parser.release()  # 释放模型

# # 语义角色分析
# srl_model_path = os.path.join(
#     LTP_DATA_DIR, 'srl')  # 语义角色标注模型目录路径，模型目录为`srl`。注意该模型路径是一个目录，而不是一个文件。

# from pyltp import SementicRoleLabeller
# labeller = SementicRoleLabeller()  # 初始化实例
# labeller.load(srl_model_path)  # 加载模型

# words = ['元芳', '你', '怎么', '看']
# postags = ['nh', 'r', 'r', 'v']
# netags = ['S-Nh', 'O', 'O', 'O']
# # arcs 使用依存句法分析的结果
# roles = labeller.label(words, postags, netags, arcs)  # 语义角色标注

# # 打印结果
# for role in roles:
#     print(role.index, "".join([
#         "%s:(%d,%d)" % (arg.name, arg.range.start, arg.range.end)
#         for arg in role.arguments
#     ]))
# labeller.release()  # 释放模型
