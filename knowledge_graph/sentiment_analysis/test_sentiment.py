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

# """ 你的 APPID AK SK """
APP_ID = '10850025'
API_KEY = 'eYAUNnDTmO7qTsSYRlvfnAqh'
SECRET_KEY = 'ZQXDsGb03HpXXawLcLIiZn1MfSkYquVN'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
engine = create_engine(
    'mysql+mysqlconnector://datatec:0.618@[172.16.103.103]:3306/JYDB',
    echo=False)

# # Create MetaData instance
# metadata = MetaData(engine, reflect=True)

# # Get Table
# ex_table = metadata.tables['C_RR_ResearchReport']
# print(ex_table)
dates = pd.date_range('2/1/2018', periods=20)
df_analysis = pd.DataFrame(columns=['datetime', 'text', 'score'])

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
    Keyword Arguments:
    df_research_articles --
    """
    df_sentiment = pd.DataFrame(columns=['datetime', 'text', 'score'])
    for item in df_research_articles.iterrows():
        print(item[0])
        #  print(item[1]['Conclusion'])
        title = item[1]['Title']

        text = item[1]['Conclusion']
        res = client.lexer(text)
        tag = client.commentTag(text)
        # 文章标签
        keyword = client.keyword(title, text)
        # 文本分类
        topic = client.topic(title, text)
        # 情感倾向分析
        sentiment = client.sentimentClassify(text)
        datetime = item[1]['InfoPublDate']
        if text:
            try:
                score = sentiment['items'][0]['sentiment']
            except KeyError:
                s = SnowNLP(text)
                score = s.sentiments * 2
            #   continue
            df_sentiment = df_sentiment.append(
                {
                    'datetime': datetime,
                    'score': score,
                    'text': text
                },
                ignore_index=True)
    return df_sentiment


def retrieve_articles(datetime, limit):
    """ retrieve articles from mysql database
    Keyword Arguments:
    datetime --
    limit    --

    Return:
    dataframe
    """
    sql_syntax = "SELECT * FROM JYDB.C_RR_ResearchReport where InfoPublDate >= '''%s''' order by InfoPublDate desc limit %s;" % (
        str(datetime), limit)
    df_research_articles = pd.read_sql(sql_syntax, engine)
    return df_research_articles


for dt in dates:
    df_articles = retrieve_articles(dt, 5)
    df = analyze_sentiment(df_articles)
    df_analysis = df_analysis.append(df, ignore_index=True)
