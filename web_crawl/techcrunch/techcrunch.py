# -*- coding: utf-8 -*-
"""
Created on Tue Jan 23 15:41:17 2018

@author: zhaohua
"""

#import __future__
#from __future__ import division
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import random
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
import os
import cchardet
import requests
from math import ceil
import datetime
import demjson

from urllib.parse import quote_plus, urlparse, parse_qs


class Techcrunch():

    def __init__(self):
        pass

    def Cold_boot(self, url):
        # 初始网页启动
        try:
            headers = {'user-agent': self.get_random_user_agent()}
            time.sleep(0.02)
            Resp2 = requests.get(url, headers)
            content = Resp2.content
            charset = cchardet.detect(content)
            html = content.decode(charset['encoding'])
            dejson = demjson.decode(html)
        except:
            return None
        return dejson

    def gain_data(self, query, nums):
        page = 1
        init_url = self.req_url(query, page)
        all_info = []
        dejsons = self.Cold_boot(init_url)
        result_counts = dejsons['info']['page']['total_result_count']
        pages = int(ceil(nums / 10))
        while page <= pages:
            print(page)
            info = self.content(dejsons)
            all_info = all_info + info
            url = self.req_url(query, page)
            dejsons = self.Cold_boot(url)
            page = page + 1
        all_infos = {
            'all_info': all_info,
            'result_counts': result_counts,
            'url': init_url
        }
        return all_infos

    def content(self, dejson):
        #####最底层内容###
        infomation = []
        if dejson['records']['page'] is not None:
            for iid in dejson['records']['page']:
                author = iid['author']
                print(author)
                content = iid['content']
                print(content)
                title = iid['title']
                print(title)
                timestamp = iid['timestamp']
                # print timestamp
                time_pub = timestamp.replace('T', ' ').replace('Z', '')
                m = datetime.datetime.strptime(time_pub, "%Y-%m-%d %H:%M:%S")
                Time = time.mktime(m.timetuple())
                # print Time
                url = iid['url']
                # print url
                # if iid['tag'] is not None:
                #     tag=iid['tag']
                #     print tag
                # print '*'*100
                infos = {
                    'author': author,
                    'content': content,
                    'title': title,
                    'Time': Time,
                    'url': url
                    # 'tag':tag
                }
                infomation.append(infos)
        else:
            pass

        return infomation

    def req_url(self, query, page, pause=2):
        time.sleep(pause)
        base_url = 'https://api.swiftype.com/api/v1/public/engines/search.json?q={query}&engine_key=zYD5B5-eXtZN9_epXvoo&page={page}&per_page=10'
        url = base_url.format(query=quote_plus(query), page=page)
        return url

    def get_data(self, filename, default=''):
        root_folder = os.path.dirname(__file__)
        user_agents_file = os.path.join(
            os.path.join(root_folder, 'data'), filename)
        try:
            with open(user_agents_file) as fp:
                data = [_.strip() for _ in fp.readlines()]
        except:
            data = [default]
        return data

    def get_random_user_agent(self):
        USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.89 Safari/537.36'

        return random.choice(self.get_data('user_agents.txt', USER_AGENT))
