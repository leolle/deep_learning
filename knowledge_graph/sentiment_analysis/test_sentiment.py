# -*- coding: utf-8 -*-
from aip import AipNlp
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
from pyltp import Segmentor
from pyltp import Postagger
from pyltp import NamedEntityRecognizer
import itertools
import matplotlib.pyplot as plt
from tqdm import tqdm

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

# """ 你的 APPID AK SK """
APP_ID = '10850025'
API_KEY = 'eYAUNnDTmO7qTsSYRlvfnAqh'
SECRET_KEY = 'ZQXDsGb03HpXXawLcLIiZn1MfSkYquVN'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
engine = create_engine(
    'mysql+mysqlconnector://datatec:0.618@[172.16.103.103]:3306/JYDB',
    echo=False)

logging.basicConfig(
    format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)

# # Create MetaData instance
# metadata = MetaData(engine, reflect=True)

# # Get Table
# ex_table = metadata.tables['C_RR_ResearchReport']
# print(ex_table)

# df_research_articles = pd.read_sql(
#     "SELECT * FROM JYDB.C_RR_ResearchReport where InfoPublDate == '''2018-02-01 00:00:00''' order by InfoPublDate desc limit 1;",
#     engine)
# for item in df_research_articles.iterrows():
#     print(item[0])
#     #  print(item[1]['Conclusion'])
#     title = item[1]['Title']

#     text = item[1]['Conclusion']
#     res = client.lexer(text)
#     tag = client.commentTag(text)
#     # 文章标签
#     keyword = client.keyword(title, text)
#     # 文本分类
#     topic = client.topic(title, text)
#     # 情感倾向分析
#     sentiment = client.sentimentClassify(text)
#     datetime = item[1]['InfoPublDate']
#     if text:
#         try:
#             score = sentiment['items'][0]['sentiment']
#         except KeyError:
#             s = SnowNLP(text)
#             score = s.sentiments * 2
#         #   continue
#         df_analysis = df_analysis.append(
#             {
#                 'datetime': datetime,
#                 'score': score,
#                 'text': text
#             },
#             ignore_index=True)


def analyze_sentiment(df_research_articles):
    """
    natural language processing on every row from the input.
    Keyword Arguments:
    df_research_articles --
    """
    df_result = pd.DataFrame(
        columns=['datetime', 'entity', 'keyword', 'summary', 'score'])
    for item in df_research_articles.iterrows():
        #  print(item[1]['Conclusion'])
        title = item[1]['Title']
        logging.info(item[0])
        logging.info(title)

        text = item[1]['Conclusion']
        #res = client.lexer(text)
        #tag = client.commentTag(text)
        # 文章标签
        #keyword = client.keyword(title, text)
        # 文本分类
        # topic = client.topic(title, text)
        # 情感倾向分析
        # sentiment = client.sentimentClassify(text)
        datetime = item[1]['InfoPublDate']
        if text:
            text_split = preprocess_string(text, filter_setting)
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
            #   continue
            ls_entity = [dict_netags[x] for x in ['B-Ni', 'E-Ni', 'I-Ni']]
            try:
                df_result = df_result.append(
                    {
                        'datetime': datetime,
                        'keyword': ','.join(s.keywords()),
                        'entity':
                        list(itertools.chain.from_iterable(ls_entity)),
                        'summary': ';'.join(s.summary()),
                        'score': score
                        # 'text': text,
                    },
                    ignore_index=True)
            except:
                continue
    return df_result


def retrieve_data(datetime, limit):
    """ retrieve articles from mysql database
    Keyword Arguments:
    datetime --
    limit    --

    Return:
    dataframe
    """
    sql_syntax = '''SELECT * FROM JYDB.C_RR_ResearchReport where WritingDate = "%s" limit %s;''' % (
        datetime.date().strftime("%Y-%m-%d"), limit)
    df_research_articles = pd.read_sql(sql_syntax, engine)
    return df_research_articles


dates = pd.date_range('1/1/2018', periods=4)
df_analysis = pd.DataFrame(
    columns=['datetime', 'entity', 'keyword', 'summary', 'score'])

# for dt in dates:
#     logging.info(dt)
#     df_articles = retrieve_articles(dt, 2)
#     df = analyze_sentiment(df_articles)
#     df_analysis = df_analysis.append(df, ignore_index=True)

# df_sentiment = df_analysis[['datetime', 'score']].groupby('datetime').mean()
# df_sentiment['count'] = df_analysis[['datetime',
#                                      'score']].groupby('datetime').count()

# index = pd.read_csv(
#     '~/share/deep_learning/data/sentiment/shangzheng_index.csv',
#     usecols=['tradeDate', 'closeindex'],
#     encoding="ISO-8859-1")
# index = index.set_index(pd.DatetimeIndex(index['tradeDate'])).drop(
#     'tradeDate', axis=1)
# index = index[index.closeindex != 0]
# index_ret = index.pct_change()
# # index_ret['sentiment'] = df_sentiment.pct_change()
# print(index_ret)

index = pd.read_csv(
    user_path + '/share/deep_learning/data/sentiment/shangzheng.csv',
    usecols=['datetime', 'return'],
    encoding="ISO-8859-1")
index = index.set_index('datetime')
# index_ret = index[index < -1.0].dropna()
index_ret = index.set_index(pd.DatetimeIndex(index.index))
dates = index_ret.index

for dt in tqdm(dates):
    logging.info(dt)
    df_articles = retrieve_data(dt, 9999)
    df = analyze_sentiment(df_articles)
    df_analysis = df_analysis.append(df, ignore_index=True)
    pre_dt = dt - pd.DateOffset(days=1)
    if pre_dt not in dates:
        logging.info(pre_dt)
        df_articles = retrieve_data(pre_dt, 9999)
        df = analyze_sentiment(df_articles)
        df_analysis = df_analysis.append(df, ignore_index=True)
df_sentiment = df_analysis[['datetime', 'score']].groupby('datetime').mean()
df_sentiment['count'] = df_analysis[['datetime',
                                     'score']].groupby('datetime').count()
df_sentiment.to_csv('sentiment.csv')
df_analysis.to_csv('article_summary.csv')
# 释放模型
postagger.release()
recognizer.release()
# df_sentiment.loc['2017-12']['score'].plot(legend=True)
# df_sentiment.loc['2017-12']['return'].plot(kind='bar')
# df_sentiment.ix['2017-12']['count'].plot(
#     secondary_y=True, style='g', legend=True)

# df_sentiment['score'].rolling(20).mean().plot()
# df_sentiment['return'].plot(secondary_y=True)
