# -*- coding: utf-8 -*-
"""
Created on Thu Jan 25 19:13:44 2018

@author: Administrator
"""
import sys
from bs4 import BeautifulSoup
from selenium import webdriver
import random
import re
import time
import os
import cchardet
import requests
from math import ceil
import datetime
# import urlparse
# if sys.version_info[0] > 2:
from urllib.parse import quote_plus, urlparse, parse_qs


class Huxiu():

    def __init__(self):
        pass


#        self.driver = webdriver.PhantomJS(executable_path=r'C:\Users\Administrator\Anaconda2\Lib\site-packages\selenium\webdriver\phantomjs\phantomjs.exe')

    def Cold_boot(self, url):
        # 初始网页启动
        try:
            print(self.get_random_user_agent())
            headers = {'User-Agent': self.get_random_user_agent()}
            #            headers = {'User-Agent': 'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)'}

            time.sleep(0.02)
            Resp2 = requests.get(url, headers=headers)
            print(Resp2)
            content = Resp2.content
            #            print content
            charset = cchardet.detect(content)
            html = content.decode(charset['encoding'])
            bsObj = BeautifulSoup(html, "lxml")
        except:
            return None
        return bsObj

    def gain_data(self, query, nums):

        all_infomation = []
        all_info = []
        pages = int(ceil(nums / 10))
        page = 0
        init_url = self.req_url(query, page=0)
        while page < pages:
            url = self.req_url(query, page=page, pause=2)
            print(url)
            bsObj = self.Cold_boot(url)
            info = self.contents(bsObj)
            all_info = all_info + info
            page = page + 1
        all_infos = {'all_info': all_info, 'url': init_url}
        all_infomation.append(all_infos)
        return all_infomation

    def contents(self, bsObj):
        #####最底层内容###
        all_data = []
        base_url = 'https://www.huxiu.com{}'
        for iid1 in bsObj.find_all('ul', class_='search-wrap-list-ul'):
            for iid in iid1.find_all('li'):
                Title = iid.find('h2').text
                link = iid.find('a').attrs['href']
                Links = base_url.format(link)
                Content = iid.find('div', class_='mob-summay').text
                time_author = iid.find('div', class_='mob-author').text
                pattern1 = re.compile(u'(\D+)')
                author = re.findall(pattern1, time_author)[0]
                pattern2 = re.compile(u'\d+-\d+-\d+ \d+:\d+')
                time1 = re.findall(pattern2, time_author)[0]
                m = datetime.datetime.strptime(time1, "%Y-%m-%d %H:%M")
                Time = time.mktime(m.timetuple())
                #        print Time
                information = {
                    'Title': Title,
                    'Links': Links,
                    'Content': Content,
                    'author': author,
                    'Time': Time
                }

                all_data.append(information)

        return all_data

    def req_url(self, query, page, pause=2):
        time.sleep(pause)
        base_url = 'https://www.huxiu.com/search.html?s={query}&sort=&per_page={page}'
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
