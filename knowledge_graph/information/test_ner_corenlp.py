# -*- coding: utf-8 -*-
"""
中英文分词: StanfordTokenizer
中英文词性标注: StanfordPOSTagger
中英文命名实体识别: StanfordNERTagger
中英文句法分析: StanfordParser
中英文依存句法分析: StanfordDependencyParser, StanfordNeuralDependencyParser
"""
# StanfordNERTagger 英文命名实体识别
from nltk.tag import StanfordNERTagger
import jieba
from preprocessing import preprocess_string
from preprocessing import strip_numeric, remove_stopwords, strip_punctuation, tokenize
from timeit import default_timer
from nltk.tag import StanfordPOSTagger
from nltk.parse.stanford import StanfordParser

en_model_file_path = '/home/weiwu/tools/stanford-ner-2017-06-09/classifiers/english.all.3class.distsim.crf.ser.gz'
ch_model_file_path = '/home/weiwu/share/software/chinese.misc.distsim.crf.ser.gz'
jar_path = '/home/weiwu/tools/stanford-ner-2017-06-09/stanford-ner-3.8.0.jar'
en_tagger = StanfordNERTagger(
    model_filename=en_model_file_path, path_to_jar=jar_path)
print(
    en_tagger.tag(
        'Rami Eid is studying at Stony Brook University in NY'.split()))
# [('Rami', 'PERSON'), ('Eid', 'PERSON'), ('is', 'O'), ('studying', 'O'), ('at', 'O'), ('Stony', 'ORGANIZATION'), ('Brook', 'ORGANIZATION'), ('University', 'ORGANIZATION'), ('in', 'O'), ('NY', 'O')]

# StanfordNERTagger 中文命名实体识别
begin = default_timer()
str_test = u'''云南铜业股份有限公司（深交所：000878），简称云铜股份、云铜，前身为云南冶炼厂，成立于1958年，1998年改制为股份公司，更名为现称，1998年6月2日于深圳证券交易所上市。公司是中国第四大铜业企业，生产高纯阴极铜、电工用铜线坏、工业硫酸、金锭、银锭、电工用圆铜线、硫酸铜等主产品，并能综合回收金、银、铝、铋、铂、钯等多种有色金属。2007年10月，中国铝业收购云铜母公司云南铜业集团的49%股权，改名“中铝云南铜业集团”。'''
filter_setting = [tokenize, strip_punctuation]
text = preprocess_string(str_test, filter_setting)
ch_tagger = StanfordNERTagger(
    model_filename=ch_model_file_path, path_to_jar=jar_path)
end = default_timer()
result = ch_tagger.tag(text.split())
for word, tag in result:
    print(word, tag)
load_duration = end - begin
print("Total procesing time: %.1fs seconds" % (end - begin))

# StanfordPOSTagger 中文词性标注
pos_tagger_model_file_path = '/home/weiwu/share/software/chinese-distsim.tagger'
pos_tagger_jar_file_path = '/home/weiwu/tools/stanford-postagger-full-2017-06-09/stanford-postagger-3.8.0.jar'

ch_pos_tagger = StanfordPOSTagger(
    model_filename=pos_tagger_model_file_path,
    path_to_jar=pos_tagger_jar_file_path)
pos_result = ch_pos_tagger.tag(text.split())

# StanfordParser 中文句法分析
path_to_jar = None
path_to_models_jar = None
model_path = 'edu/stanford/nlp/models/lexparser/englishPCFG.ser.gz'
ch_parser = StanfordParser(
    r"E:\tools\stanfordNLTK\jar\stanford-parser.jar",
    r"E:\tools\stanfordNLTK\jar\stanford-parser-3.6.0-models.jar",
    r"E:\tools\stanfordNLTK\jar\classifiers\chinesePCFG.ser.gz")
