import os
import random
import sys
import time
import re
import cchardet
import requests
import pandas as pd
import bs4
from bs4 import BeautifulSoup
from pandas import DataFrame
from math import ceil
import config

from config import USER_AGENT,  URL_SEARCH, LOGGER

if sys.version_info[0] > 2:
    from urllib.parse import quote_plus, urlparse, parse_qs
else:
    from urllib import quote_plus
    from urlparse import urlparse, parse_qs


class Weixinsogou():
    """
    Weixinsogou search.
    """
    
    def __init__(self, proxies=None):
        self.proxies = random.choice(proxies) 
        if proxies :pass
        else :None
        
        
    def counts_result(self, bsObj):      
        breif_counts= bsObj.find_all('div',class_='mun')[0].text
        pattern=re.compile(u'(\d+)')
        result_counts= int(re.findall(pattern,breif_counts)[0])
        return result_counts



    def content(self, bsObj,pause=2):
        infomation=[]
        for item in bsObj.find_all('ul',class_='news-list'):
            for iid in item.find_all('li'):
                contents= iid.find_all('div',class_='txt-box')[0]
                Link= contents.find('a').attrs['href']
                Title= contents.find('a').text
                Abstract=iid.find_all('p',class_='txt-info')[0].text
                author_time=iid.find_all('a',class_='account')[0]
                source_link= author_time.attrs['href']
                Source=author_time.text
                timeConvert=iid.find('span','s2').text
                pattern=re.compile(u'(\d+)')
                Time= int(re.findall(pattern,timeConvert)[0])
                
                infos={
                'Link':Link,
                'Title':Title,
                'Abstract':Abstract,
                'source_link':source_link,
                'Source':Source,
                'Time':Time
                   }
                infomation.append(infos)  
        return infomation 

    
    def req_url(self, query, page, pause=2):
        time.sleep(pause)
        url = URL_SEARCH
        url = url.format(query=quote_plus(query),page=page)
        return url

    def Cold_boot(self, url, pause=2):
        
        time.sleep(pause)
        headers = {'user-agent': self.get_random_user_agent()}
        try:
            requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
            r = requests.get(url=url,
                             proxies=self.proxies,
                             headers=headers,
                             allow_redirects=False,
                             verify=False,
                             timeout=30)
            LOGGER.info(url)
            content = r.content
            charset = cchardet.detect(content)
            text = content.decode(charset['encoding'])
            bsObj = BeautifulSoup(text, "lxml")
            return bsObj
        except Exception as e:
            LOGGER.exception(e)
            return None

    

    def get_random_user_agent(self):
        """
        Get a random user agent string.
        :return: Random user agent string.
        """
        return random.choice(self.get_data('user_agents.txt', USER_AGENT))




    def gain_data(self, query, nums=None,pause=2):
        page=1
        url=self.req_url(query, page, pause=2)
        bsObj=self.Cold_boot(url)
        total_count=self.counts_result(bsObj)
        pages=int(ceil(nums/10))
        page=1
        all_info=[]
        while page<pages:
            print page 
            url=self.req_url(query, page, pause=2)
            print url
            bsObj=self.Cold_boot(url)
            info=self.content(bsObj,pause=2)
            all_info=all_info+info
            page=page+1
        infos={
        'total_count':total_count,
        'url':url,
        'all_info':all_info
        }                    
        return infos

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

     


        

