# -*- coding: utf-8 -*-
"""
中英文分词: StanfordTokenizer
中英文词性标注: StanfordPOSTagger
中英文命名实体识别: StanfordNERTagger
中英文句法分析: StanfordParser
中英文依存句法分析: StanfordDependencyParser, StanfordNeuralDependencyParser
"""
from preprocessing import preprocess_string
from preprocessing import strip_numeric, remove_stopwords, strip_punctuation, tokenize
from timeit import default_timer
from stanfordcorenlp import StanfordCoreNLP

begin = default_timer()
str_test = u'''云南铜业股份有限公司（深交所：000878），简称云铜股份、云铜，前身为云南冶炼厂，成立于1958年，1998年改制为股份公司，更名为现称，1998年6月2日于深圳证券交易所上市。公司是中国第四大铜业企业，生产高纯阴极铜、电工用铜线坏、工业硫酸、金锭、银锭、电工用圆铜线、硫酸铜等主产品，并能综合回收金、银、铝、铋、铂、钯等多种有色金属。2007年10月，中国铝业收购云铜母公司云南铜业集团的49%股权，改名“中铝云南铜业集团”。'''
filter_setting = [tokenize, strip_punctuation]
text = preprocess_string(str_test, filter_setting)
nlp = StanfordCoreNLP(
    '/home/weiwu/tools/stanford-corenlp-full-2017-06-09/', lang='zh')
tokenize = nlp.word_tokenize(str_test)
pos_tag = nlp.pos_tag(str_test)
ner = nlp.ner(str_test)
parse = nlp.parse(str_test)
depend = nlp.dependency_parse(str_test)
end = default_timer()
