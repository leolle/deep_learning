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
# import urlparse
import demjson

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    # from urlparse import urlparse, parse_qs


class Xueqiu():

    def __init__(self):
        pass

    def Cold_boot(self, url):
        # 初始网页启动
        try:
            cookies = {
                'Cookie':
                'device_id=7fcd4c28ad0e89ba428a8c56a4453d31; s=ff14amelyq; webp=0; bid=345537d98b511672eaec478c4fcd5981_j78it1r0; u=601519629157904; xq_a_token=19f5e0044f535b6b1446bb8ae1da980a48bbe850; xq_r_token=6d30415b5f855c12fd74c6e2fb7662ea40272056; Hm_lvt_1db88642e346389874251b5a1eded6e3=1519955346,1520561220,1520735671,1520738899; aliyungf_tc=AQAAAJLO6SRs6wwA2nGotP+HuHu9OY52; __utma=1.1948606804.1520756528.1520756528.1520756528.1; __utmc=1; __utmz=1.1520756528.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utmt=1; __utmb=1.1.10.1520756528; Hm_lpvt_1db88642e346389874251b5a1eded6e3=1520756528'
            }
            headers = {'user-agent': self.get_random_user_agent()}
            time.sleep(0.02)
            Resp2 = requests.get(url, headers=headers, cookies=cookies)
            content = Resp2.content
            charset = cchardet.detect(content)
            html = content.decode(charset['encoding'])
            dejson = demjson.decode(html)
        except:
            return None
        return dejson

    def gain_data(self, query, nums):
        page = 1
        link = 'https://xueqiu.com/k?q={query}'
        init_url = self.req_url(query, page)
        all_info = []
        dejsons = self.Cold_boot(init_url)
        result_counts = dejsons['count']
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
            'url': link
        }
        return all_infos

    def content(self, dejson):
        #####最底层内容###
        infomation = []
        base_url = 'https://xueqiu.com/u/{}'
        for iid in dejson['list']:

            title = iid['title']
            Title = BeautifulSoup(title, "lxml").text
            # print Title

            created_at = iid['created_at']
            # print created_at

            reply_count = iid['reply_count']
            # print reply_count

            like_count = iid['like_count']
            # print like_count

            retweet_count = iid['retweet_count']
            # print retweet_count

            description = iid['description']
            Description = BeautifulSoup(description, "lxml").text
            # print Description
            item = iid['user']['id']
            profile = base_url.format(item)
            # print profile
            screen_name = iid['user']['screen_name']
            # print screen_name
            # print '*' * 100

            infos = {
                'Title': Title,
                'created_at': created_at,
                'reply_count': reply_count,
                'like_count': like_count,
                'retweet_count': retweet_count,
                'Description': Description,
                'profile': profile,
                'screen_name': screen_name
            }
            infomation.append(infos)

        return infomation

    def req_url(self, query, page, pause=2):
        time.sleep(pause)
        base_url = 'https://xueqiu.com/statuses/search.json?sort=relevance&source=all&q={query}&count=10&page={page}'
        url = base_url.format(query=quote_plus(query), page=page)
        # print url
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
