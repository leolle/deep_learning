# -*- coding: utf-8 -*-
from pymongo import MongoClient
from pymongo.errors import DuplicateKeyError
from google_search.magic_google import MagicGoogle as GoogleSearch
from google_news.news import MagicGoogle_News as GoogleNews
from xueqiu import Xueqiu
import pandas as pd
import networkx as nx
from ylib import ylog
import logging

ylog.set_level(logging.DEBUG)
ylog.console_on()
ylog.filelog_on("app")

client = MongoClient('mongodb://localhost:27017/')
db = client['sentiment']
mongo_client = db.xueqiu

new_kw = 'china 50'

gs = GoogleSearch()
data = gs.gain_data(query=new_kw, language='en', nums=10)
print(data['RelatedKeywords'])

mg = Xueqiu.Xueqiu()
query = '创业板'
query_list = ['创业板', '上证', '深证']


def get_data(source, query, num=1000):
    """ get source using query as target keyword, return text content.
    Keyword Arguments:
    source --
    query  --
    """
    infos = source.gain_data(query=query, nums=num)
    return infos['all_info']


for q in query_list:
    crawl_data = get_data(mg, q)
    for post in crawl_data:
        # insert data
        try:
            # mongo_client.insert_one(post)
            post['name'] = q
            mongo_client.update(post, post, upsert=True)
        except DuplicateKeyError:
            continue

infos = mg.gain_data(query=query, nums=1000)

df_sentiment = pd.DataFrame(infos['all_info'])
df_sentiment = df_sentiment.set_index(
    pd.DatetimeIndex(df_sentiment['created_at'])).drop(
        'created_at', axis=1)
df_sentiment = df_sentiment.sort_index()

for post in infos['all_info']:
    # insert data
    try:
        # mongo_client.insert_one(post)
        post['name'] = query
        mongo_client.update(post, post, upsert=True)
    except DuplicateKeyError:
        continue
# gn = GoogleNews()
# data = gn.gain_data(query=new_kw, language='en', nums=100)

# mg = Xueqiu()
# infos = mg.gain_data(query='创业板 2018-03-11', nums=260)


def main():
    mg = Xueqiu.Xueqiu()
    infos = mg.gain_data(query='华通热力 2017 2016', nums=1)
    print(infos)


if __name__ == '__main__':
    main()

gs = GoogleSearch()
data = gs.gain_data(query=new_kw, language='en', nums=1)
base_nodes = data['RelatedKeywords']
logging.debug('base nodes %s' % base_nodes)

# logging.debug(base_nodes)
# while i < depth:
#     for index, b in enumerate(base_nodes):
#         if b not in graph:
#             logging.debug('crawling %s' % b)
#             data = gs.gain_data(query=b, language='en', nums=1)
#             nodes = data['RelatedKeywords']
#         else:
#             nodes = []
#         logging.debug("new nodes %s" % nodes)
#         end_nodes.extend(nodes)
#         if len(nodes) > 0:
#             for n in nodes:
#                 graph.add_edge(b, n)
#     base_nodes = copy.copy(end_nodes)
#     logging.debug('level %s nodes: %s' % (i, end_nodes))
#     end_nodes = []
#     i += 1

# ls_nodes = list(graph.nodes)
# counter = 0
# total_nodes_num = len(graph.nodes)
# rm_counter = 0
