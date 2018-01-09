# -*- coding: utf-8 -*-
import sys
from gensim.models import KeyedVectors
import logging
import jieba
import codecs

punct = set(u''':!),.:;?]}¢'"、。〉》」』】〕〗〞︰︱︳﹐､﹒
﹔﹕﹖﹗﹚﹜﹞！），．：；？｜｝︴︶︸︺︼︾﹀﹂﹄﹏､～￠
々‖•·ˇˉ―--′’”([{£¥'"‵〈《「『【〔〖（［｛￡￥〝︵︷︹︻
︽︿﹁﹃﹙﹛﹝（｛“‘-—_…''')
stopwords = codecs.open('stopwords', 'r', 'utf-8').read().split()

filterpunt = lambda s: ''.join(filter(lambda x: x not in punct, s))
topn = 20


def similar_words(text, zh_model, en_model, topn=topn):
    """ input a text, return every word's similar words
    Keyword Arguments:
    text     --
    zh_model --
    en_model --
    """

    filterpunt_text = filterpunt(text)
    tokens_generator = jieba.cut(filterpunt_text)
    tokens = [
        x for x in tokens_generator if not x.isspace() and x not in stopwords
    ]
    results = {}
    for token in tokens:
        result = []
        # print token
        if token in zh_model:
            result = zh_model.most_similar(token, topn=topn)
        elif token in en_model:
            result = en_model.most_similar(token, topn=topn)
        if result:
            results[token] = [x[0] for x in result]
    return results


if __name__ == '__main__':
    # if len(sys.argv) != 3:
    #     print("Please use python demo.py input_text > output_text")
    #     exit()
    input_path = sys.argv[1]

    with open(input_path, 'r') as f:
        input_text = f.readline()
    logger = logging.getLogger()
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s %(name)-12s %(levelname)-8s %(message)s')
    handler.setFormatter(formatter)
    if not logger.handlers:
        logger.addHandler(handler)
        logger.setLevel(logging.DEBUG)
    en_model_filename = './en_model'
    zh_model_filename = './zh_model'
    zh_model = KeyedVectors.load_word2vec_format(
        zh_model_filename, binary=False)
    en_model = KeyedVectors.load_word2vec_format(
        en_model_filename, binary=False)
    # input_text = u'read investment research document and, 建立量化研究盈利因子的模型.'
    output = similar_words(
        input_text, zh_model=zh_model, en_model=en_model, topn=topn)
    for item in output:
        print(item.encode('utf-8') + ':')
        for word in output[item]:
            print(word.encode('utf-8'))
        print('\n')
