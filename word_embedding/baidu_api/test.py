# -*- coding: utf-8 -*-
from aip import AipNlp
from sqlalchemy import create_engine
from sqlalchemy import MetaData
from sqlalchemy import Table
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
import numpy as np
import pandas as pd
from ylib import ylog
from requests.exceptions import ConnectionError, ChunkedEncodingError

# """ 你的 APPID AK SK """
APP_ID = '10850025'
API_KEY = 'eYAUNnDTmO7qTsSYRlvfnAqh'
SECRET_KEY = 'ZQXDsGb03HpXXawLcLIiZn1MfSkYquVN'

client = AipNlp(APP_ID, API_KEY, SECRET_KEY)
engine = create_engine(
    'mysql+mysqlconnector://datatec:0.618@[172.16.103.103]:3306/JYDB',
    echo=False)

# Create MetaData instance
metadata = MetaData(engine, reflect=True)
# print(metadata.tables)

# Get Table
ex_table = metadata.tables['C_RR_ResearchReport']
print(ex_table)

Base = automap_base()
Base.prepare(engine, reflect=True)
research_tbl = Base.classes.C_RR_ResearchReport
session = Session(engine)
query = session.query(research_tbl)

# text = "市场价值最高的A股股票，市盈率，股息"
# text = "云南铜业股份有限公司（深交所：000878），简称云铜股份"
# text = u'''云南铜业股份有限公司（深交所：000878），简称云铜股份、云铜'''
# """ 调用词法分析 """
# res = client.lexer(text)
# # print(res)
# options = {}
# options["type"] = 8
# print(client.commentTag(text, options))
# print(client.topic(text[:10], text))
