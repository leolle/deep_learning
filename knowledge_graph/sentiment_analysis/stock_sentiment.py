# -*- coding: utf-8 -*-
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import Table
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from ylib import ylog
from requests.exceptions import ConnectionError, ChunkedEncodingError
from snownlp import SnowNLP
import logging
from pyltp import SentenceSplitter
from ylib.preprocessing import preprocess_string
from ylib.preprocessing import strip_numeric
from ylib.preprocessing import remove_stopwords
from ylib.preprocessing import strip_punctuation
from ylib.preprocessing import tokenize
from collections import defaultdict
from timeit import default_timer
import os
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
import itertools
import matplotlib.pyplot as plt
from tqdm import tqdm
import datetime

filter_setting = [tokenize, strip_punctuation]
user_path = os.path.expanduser("~")

LTP_DATA_DIR = user_path + '/share/software/ltp_data_v3.4.0'  # ltp模型目录的路径

# 词性标注
pos_model_path = os.path.join(LTP_DATA_DIR,
                              'pos.model')  # 词性标注模型路径，模型名称为`pos.model`
postagger = Postagger()  # 初始化实例
postagger.load(pos_model_path)  # 加载模型

# 命名实体识别
ner_model_path = os.path.join(LTP_DATA_DIR,
                              'ner.model')  # 命名实体识别模型路径，模型名称为`pos.model`

recognizer = NamedEntityRecognizer()  # 初始化实例
recognizer.load(ner_model_path)  # 加载模型

engine = create_engine(
    'mysql+mysqlconnector://datatec:0.618@[172.16.103.103]:3306/JYDB',
    echo=False)

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

df_analyst_report = pd.read_pickle(
    user_path + '/share/deep_learning/data/sentiment/df_analyst_report.pkl')


def analyze_sentiment(df_text):
    """
    natural language processing on every row from the input.
    1. for loop dataframe:
    2. preprocess text in the df.
    3. get entity using pyLTP
    4. get sentiment, keywords, summary using SnowNLP.
    5. append result to df
    Keyword Arguments:
    df_text --
    """
    df_result = pd.DataFrame(columns=[
        'datetime', 'people', 'geography', 'organization', 'keyword', 'summary',
        'score'
    ])
    for item in df_text.iterrows():
        #  print(item[1]['Conclusion'])
        logging.info(item[0])

        text = item[1]['Conclusion']
        datetime = item[1]['WritingDate']
        if not pd.isnull(text):
            text_split = preprocess_string(text)
            # 词性标注
            #            postagger = Postagger()  # 初始化实例

            words = text_split.split()  # 分词结果
            postags = postagger.postag(words)  # 词性标注

            # 命名实体识别

            #            recognizer = NamedEntityRecognizer()  # 初始化实例

            netags = recognizer.recognize(words, postags)  # 命名实体识别

            dict_netags = defaultdict(list)
            ls_netags = list(zip(netags, words))
            for x, y in ls_netags:
                dict_netags[x].append(y)

            s = SnowNLP(text)
            score = s.sentiments * 2
            # # 人名（Nh）、地名（Ns）、机构名（Ni。）
            # # B、I、E、S
            ls_organization = [
                dict_netags[x] for x in ['S-Ni', 'B-Ni', 'E-Ni', 'I-Ni']
            ]
            ls_people = [
                dict_netags[x] for x in ['S-Nh', 'B-Nh', 'E-Nh', 'I-Nh']
            ]
            ls_geography = [
                dict_netags[x] for x in ['S-Ns', 'B-Ns', 'E-Ns', 'I-Ns']
            ]
            try:
                df_result = df_result.append(
                    {
                        'datetime':
                        datetime,
                        'keyword':
                        ','.join(s.keywords()),
                        'organization':
                        list(itertools.chain.from_iterable(ls_organization)),
                        'people':
                        list(itertools.chain.from_iterable(ls_people)),
                        'geography':
                        list(itertools.chain.from_iterable(ls_geography)),
                        'summary':
                        ';'.join(s.summary()),
                        'score':
                        score
                        # 'text': text,
                    },
                    ignore_index=True)
            except:
                continue
    return df_result


# # 人名（Nh）、地名（Ns）、机构名（Ni。）
# # B、I、E、S
# ls_organization = [dict_netags[x] for x in ['S-Ni', 'B-Ni', 'E-Ni', 'I-Ni']]
# ls_people = [dict_netags[x] for x in ['S-Nh', 'B-Nh', 'E-Nh', 'I-Nh']]
# ls_geography = [dict_netags[x] for x in ['S-Ns', 'B-Ns', 'E-Ns', 'I-Ns']]

df_result = analyze_sentiment(df_analyst_report[:100])
df_result.to_pickle('df_sentiment.pkl')
organization = None
# organization = '中通'
people = '亿元'
# people = '刘士余'

geography = None
# geography = '中国'
# date = pd.to_datetime('20170308', format='%Y%m%d', errors='ignore')
date = pd.date_range(start='2017-10-25', end='20171026')
if people or organization or geography:
    df_filter = df_result[df_result.apply(
        lambda row: people in row.people or organization in row.organization or geography in row.geography,
        axis=1)]
# elif
# df_filter = df_result[df_result.apply(
#     lambda row: organization in row.organization, axis=1)]

df_sentiment = df_filter[['datetime', 'score']].groupby('datetime').mean()
df_sentiment['count'] = df_filter[['datetime',
                                   'score']].groupby('datetime').count()

print(df_sentiment.ix[date])
