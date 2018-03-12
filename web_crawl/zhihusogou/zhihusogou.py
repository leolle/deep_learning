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


class Zhihusogou():
    """
    Zhihusogou search.
    """
    
    def __init__(self, proxies=None):
        self.proxies = random.choice(proxies) 
        if proxies :pass
        else :None
        
        


    def content(self, bsObj,pause=2):
        infomation=[]
        for item in bsObj.find_all('div',class_='box-result'):
        #    print item
            for iid in item.find_all('div',class_='result-about-list'):
                user_1=None
                user_2=None
                contxts=None
                Link=None
                anwser_counts=0
                anwser_link=None
                favorate_counts=0
                Title=None
                
                if len( iid.find_all('div',class_='about-text'))!=0:
                    contxts= iid.find_all('div',class_='about-text')[0].find_all('a',class_='link-white-pre')[0].text
                    print contxts
           
                contents= iid.find_all('h4',class_='about-list-title')[0]
                Link= contents.find('a').attrs['href']
                print Link
                Title= contents.find('a').text
                print Title
                if len(iid.find_all('p',class_='about-answer'))!=0:
                    Abstract=iid.find_all('p',class_='about-answer')[0]
            #        print Abstract
                    favorate_txt= Abstract.find_all('span',class_='count')[0].text
                    pattern=re.compile(u'(\d+)')
                    favorate_counts= int(re.findall(pattern,favorate_txt)[0])
    
                    if len(Abstract.find_all('cite'))!=0:
                        user_1= Abstract.find_all('cite')[0].text
                        print user_1
                    if len(Abstract.find_all('a'))!=0:
                        user_2= Abstract.find_all('a')[0].text
                        print user_2
                if len(iid.find_all('span',class_='answer-num'))!=0:
                    Anwser_content= iid.find_all('span',class_='answer-num')[0]
                    anwser_link= Anwser_content.find('a').attrs['href']
                    print anwser_link
                    anwser_txt=Anwser_content.find('a').text
                    pattern=re.compile(u'(\d+)')
                    anwser_counts= int(re.findall(pattern,anwser_txt)[0])
                    print anwser_counts
                print '*'*50
                
                infos={
                'Link':Link,
                'Title':Title,
                'contxts':contxts,
                'favorate_counts':favorate_counts,
                'user_1':user_1,
                'anwser_link':anwser_link,
                'anwser_counts':anwser_counts,
                'user_2':user_2

                   }
                # information=infos+information
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
            time.sleep(pause)
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
        init_url=self.req_url(query, page, pause=2)
        bsObj=self.Cold_boot(init_url)
        pages=int(ceil(nums/10))
        all_info=[]
        while page<=pages:
            print page 
            url=self.req_url(query, page, pause=2)
            print url
            bsObj=self.Cold_boot(url)
            info=self.content(bsObj,pause=2)
            all_info=all_info+info
            page=page+1
        infos={
        'url':init_url,
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

     


        

