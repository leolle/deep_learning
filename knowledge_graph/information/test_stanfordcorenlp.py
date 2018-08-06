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

from stanfordcorenlp import StanfordCoreNLP
import logging
import json
from collections import defaultdict


class StanfordNLP:

    def __init__(self, host='http://localhost', port=9000):
        self.nlp = StanfordCoreNLP(
            host, port=port,
            timeout=30000)  # , quiet=False, logging_level=logging.DEBUG)
        self.props = {
            'annotators':
            'tokenize,ssplit,pos,lemma,ner,parse,depparse,dcoref,relation',
            'pipelineLanguage':
            'en',
            'outputFormat':
            'json'
        }

    def word_tokenize(self, sentence):
        return self.nlp.word_tokenize(sentence)

    def pos(self, sentence):
        return self.nlp.pos_tag(sentence)

    def ner(self, sentence):
        return self.nlp.ner(sentence)

    def parse(self, sentence):
        return self.nlp.parse(sentence)

    def dependency_parse(self, sentence):
        return self.nlp.dependency_parse(sentence)

    def annotate(self, sentence):
        return json.loads(self.nlp.annotate(sentence, properties=self.props))

    @staticmethod
    def tokens_to_dict(_tokens):
        tokens = defaultdict(dict)
        for token in _tokens:
            tokens[int(token['index'])] = {
                'word': token['word'],
                'lemma': token['lemma'],
                'pos': token['pos'],
                'ner': token['ner']
            }
        return tokens


if __name__ == '__main__':
    sNLP = StanfordNLP()
    text = 'A blog post using Stanford CoreNLP Server. Visit www.khalidalnajjar.com for more details.'
    print("Annotate:", sNLP.annotate(text))
    print("POS:", sNLP.pos(text))
    print("Tokens:", sNLP.word_tokenize(text))
    print("NER:", sNLP.ner(text))
    print("Parse:", sNLP.parse(text))
    print("Dep Parse:", sNLP.dependency_parse(text))
